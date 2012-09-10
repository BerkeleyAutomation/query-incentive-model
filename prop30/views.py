from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core.context_processors import csrf
from django.shortcuts import redirect
import settings
import os
import string
import random
import md5
import math
from recaptcha.client import captcha 

#compat fix for old servers (like heidegger)
try:
    import json
except ImportError:
    import simplejson as json
	
from models import *

"""
This view loads the index file, it also contains various logic to display
errors
"""
def index(request,parent="",errors=""):
	t = loader.get_template('index.html')
	error_type = request.session.get('errors','') #pass the error type in the session struct
	if error_type == 'email':
		errors = 'Invalid Email'
	elif error_type == 'captcha':
		errors = 'You entered the captcha incorrectly'
		
	c = RequestContext(request, {'csrf_token':csrf(request)['csrf_token'],'parent':parent,'userc':settings.USE_RECAPTCHA,'rcpk':settings.RECAPTCHA_PUBLIC_KEY, 'counter': Person.objects.all().count(), 'error': errors, 'url':settings.URL_ROOT})
	return HttpResponse(t.render(c))

"""
Uses django's form vaildator to test emails
"""
def is_valid_email(email):
	from django import forms
	from django.core.validators import ValidationError
	f = forms.EmailField()
	try:
		query= f.clean(email)
		return True
	except ValidationError:
		return False

"""
Online update of the influence score for each parent
"""
def update_score(node):
	level = 0
	current_node = node.parent_node
	while level < settings.PROPAGATION_LIMIT and current_node != None:
		current_node.influence = 1*math.pow(settings.PARENT_CHILD_DECAY_RATE,-level) + current_node.influence
		current_node.save()
		current_node = current_node.parent_node
		level = level + 1

"""
Is this post a save rating post?
"""
def is_rating_post(request):
	return request.POST.get('slider1',-1) != -1 and request.POST.get('link','') != ''

"""
Save the rating for the user
"""
def save_rating(request):
	t = loader.get_template('save.html')
	link = request.POST.get('link','');
	id = link.split('/')[len(link.split('/'))-1]
	score_link = settings.URL_ROOT+'score/'+id
	c = RequestContext(request, {'link': link,'score_link': score_link,'csrf_token':csrf(request)['csrf_token'], 'url':settings.URL_ROOT,'saved':'Saved!','slider': request.POST.get('slider1',0),'dup':request.POST.get('dup',False)})
	p = Person.objects.filter(email=request.session['email'])
	if len(p)>0:
		rating = Rating(person = p[0],rating=request.POST.get('slider1',0), session_key=str(request.session.session_key))
		rating.save()
	return HttpResponse(t.render(c))

"""
Save a child node in the tree and update the score
"""
def save_child(request,parent=None,parentString=''):
	request.session['errors'] = ''
	if settings.USE_RECAPTCHA:
		response = captcha.submit(request.POST.get('recaptcha_challenge_field'),request.POST.get('recaptcha_response_field'),settings.RECAPTCHA_PRIVATE_KEY,request.META['REMOTE_ADDR']) 
		if not response.is_valid:
			request.session['errors'] = 'captcha'
			return redirect(settings.URL_ROOT+parentString)

	email = request.POST.get('email', '')
	request.session['email'] = email
	if not is_valid_email(email):
		request.session['errors'] = 'email'
		return redirect(settings.URL_ROOT+parentString) #invalid email, send back to start
	hash = hash_email(email)
	ip = request.META.get('REMOTE_ADDR')
	slider = 50
	newp = Person.objects.filter(email = email)
	dup = (len(newp) > 0)
	if dup:
		newp = newp[0]
		rating = Rating.objects.filter(person = newp)
		if len(rating) > 0:
			slider = rating[0].rating
	else:
		if parent == None or len(parent) == 0:
			newp = Person(email = email, hash = hash, ipaddress=ip, influence=0,parent_node=None,session_key=str(request.session.session_key))
			newp.save()
		else:
			newp = Person(email = email, hash = hash, ipaddress=ip, parent=parent[0].email,parent_node=parent[0],influence=0, session_key=str(request.session.session_key))
			newp.save()
			update_score(newp)
	t = loader.get_template('save.html')
	c = RequestContext(request, {'link':settings.URL_ROOT+str(newp.id),'score_link':settings.URL_ROOT+'score/'+str(newp.id),'csrf_token':csrf(request)['csrf_token'],'url':settings.URL_ROOT,'saved': '','slider': slider,'dup':dup})
	return HttpResponse(t.render(c))
	
"""
convert the email into a hash, if we ever need privacy handling
"""
def hash_email(email):
	m = md5.new()
	m.update(email)
	return m.hexdigest()
		
"""
Actually handles the save, the logic is very important
Since functionality was built incrementally there is a 
lot of duplicate logic, should be modularized
"""
def save(request,parent=""):
	if request.method == 'GET':#If a user arrives at the save view redirect them to the main page
		return redirect(settings.URL_ROOT)
	else:
		if is_rating_post(request):#if the slider flag is set, then we know it is a slider save
	 		return save_rating(request)
			
		parentString = parent #figures out the parent from the link 
		try:
			parentInt = int(parent)
		except ValueError:
			parentInt = 0
		parent = Person.objects.filter(id=parentInt)	
		
		return save_child(request,parent,parentString)

"""
This view will ultimately dump the data in a json format
"""
def data(request,root=""):
	output = {}
	try:
		int(root)
	except ValueError:
		return HttpResponse("Error Invalid User: "+ root)

	person = Person.objects.filter(id = root)
	if len(person) == 0:
		return HttpResponse("Error Invalid User: "+ root)
	output['rank']=Person.objects.filter(influence__gte=person[0].influence).count()
	output['max_rank']=Person.objects.all().count()
	output['score']=person[0].influence
	output['top_score']=person[0].influence
	request.session['level'] = 0
	output['tree']=json.dumps(tree_to_dict(person[0],request))
	output['url'] = settings.URL_ROOT
	output['level'] = request.session['level']
	t = loader.get_template('score.html')
	c = RequestContext(request, output)
	return HttpResponse(t.render(c))

"""
Generates a dict of the tree for plotting
"""
def tree_to_dict(root,request,level=1):
	output = {'name': root.hash[0:6], 'children':[]}
	children = root.person_set.all()
	if level > request.session['level']:
		request.session['level'] = level
	if children == None or level >= settings.MAX_CHILD_LEVELS:
		return output
	for child in children:
		output['children'].append(tree_to_dict(child,request,level+1))
	return output

"""
Handles the about view.
"""
def about(request,dummy=""):
	t = loader.get_template('about.html')
	c = RequestContext(request, {'url':settings.URL_ROOT})
	return HttpResponse(t.render(c))


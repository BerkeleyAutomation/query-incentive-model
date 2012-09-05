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
import simplejson as json
from models import *

"""
This view loads the index file, it also contains various logic to display
errors
"""
def index(request,parent="",errors=""):
	t = loader.get_template('index.html')
	if request.GET.get('errors','')=='email':
		errors = 'Invalid Email'
	elif request.GET.get('errors','')=='dup':
		p = Person.objects.filter(email = request.GET.get('mail',''))
		if len(p) > 0:
			link = settings.URL_ROOT+str(p[0].id)
			errors = 'You have already submitted your email. Your Custom Link is: ' + link
		else:
			errors = 'You have already submitted your email.'

	c = RequestContext(request, {'csrf_token':csrf(request)['csrf_token'],'parent':parent, 'counter': Person.objects.all().count(), 'error': errors, 'url':settings.URL_ROOT})
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
Actually handles the save, the logic is very important
Since functionality was built incrementally there is a 
lot of duplicate logic, should be modularized
"""
def save(request,parent=""):
	if request.method == 'GET':#If a user arrives at the save view redirect them to the main page
		return redirect(settings.URL_ROOT)
	else:
		if request.POST.get('slider1',-1) != -1 and request.POST.get('link','') != '':#if the slider flag is set, then we know it is a slider save
	 		t = loader.get_template('save.html')
			c = RequestContext(request, {'link': request.POST.get('link',''),'csrf_token':csrf(request)['csrf_token'], 'url':settings.URL_ROOT,'saved':'Saved!','slider': request.POST.get('slider1',0),'dup':request.POST.get('dup',False)})
			link = request.POST.get('link','');
			id = link.split('/')[len(link.split('/'))-1]
			p = Person.objects.filter(id=id,email=request.session['email'])#for security reasons we use the cookie, id is there for speed
			if len(p)>0:
				rating = Rating(person = p[0],rating=request.POST.get('slider1',0), session_key=str(request.session.session_key))
				rating.save()
			return HttpResponse(t.render(c))
			
		parentString = parent #figures out the parent from the link 
		try:
			parentInt = int(parent)
		except ValueError:
			parentInt = 0

		parent = Person.objects.filter(id=parentInt)	
		if len(parent) == 0:
			email = request.POST.get('email', '')
			request.session['email'] = email
			if is_valid_email(email):
				m = md5.new()
                                m.update(email)
                                hash = m.hexdigest()
				ip = request.META.get('REMOTE_ADDR')
				dup = False
				slider = 50
				if Person.objects.filter(email = email).count() > 0:
					dup = True
					newp = Person.objects.filter(email = email)[0]
					rating = Rating.objects.filter(person = newp)
					if len(rating) > 0:
						slider = rating[0].rating
				else:
					dup = False
					newp = Person(email = email, hash = hash, ipaddress=ip, influence=0,parent_node=None,session_key=str(request.session.session_key))
					newp.save()
				t = loader.get_template('save.html')
				c = RequestContext(request, {'link':settings.URL_ROOT+str(newp.id),'csrf_token':csrf(request)['csrf_token'], 'url':settings.URL_ROOT,'saved': '','slider': slider,'dup':dup})
        			return HttpResponse(t.render(c))
			else:
				return redirect(settings.URL_ROOT+'?errors=email') #invalid email, send back to start
		else:
			email = request.POST.get('email', '')
			request.session['email'] = email
                        if is_valid_email(email):
				m = md5.new()
                                m.update(email)
                                hash = m.hexdigest()
                                ip = request.META.get('REMOTE_ADDR')
				dup = False
				slider = 50
				if Person.objects.filter(email = email).count() > 0:
					dup = True
					newp = Person.objects.filter(email = email)[0]
					rating = Rating.objects.filter(person = newp)
					if len(rating) > 0:
						slider = rating[0].rating
				else:
					dup = False
					newp = Person(email = email, hash = hash, ipaddress=ip, parent=parent[0].email,parent_node=parent[0],influence=0, session_key=str(request.session.session_key))
					newp.save()
					update_score(newp)
                                t = loader.get_template('save.html')
                                c = RequestContext(request, {'link':settings.URL_ROOT+str(newp.id),'csrf_token':csrf(request)['csrf_token'],'url':settings.URL_ROOT,'saved': '','slider': slider,'dup':dup})
                                return HttpResponse(t.render(c))
                        else:
                               return redirect(settings.URL_ROOT+parentString+'?errors=email') #invalid email, send back to start

"""
This view will ultimately dump the data in a json format
"""
def data(request,root=""):
	output = {}
	rankings = list(Person.objects.all().order_by('influence').reverse())

	try:
		int(root)
	except ValueError:
		return HttpResponse("Error Invalid User: "+ root)

	person = Person.objects.filter(id = root)
	if len(person) == 0:
		return HttpResponse("Error Invalid User: "+ root)
	output['rank']=rankings.index(person[0]) + 1
	output['max_rank']=len(rankings)
	output['score']=person[0].influence
	output['top_score']=rankings[0].influence
	output['tree']=json.dumps(tree_to_dict(person[0]))
	output['url'] = settings.URL_ROOT
	t = loader.get_template('score.html')
	c = RequestContext(request, output)
	return HttpResponse(t.render(c))

def tree_to_dict(root):
	output = {'name': root.hash[0:6], 'children':[]}
	children = Person.objects.filter(parent_node=root)
	if len(children) == 0:
		return output
	for child in children:
		output['children'].append(tree_to_dict(child))
	return output

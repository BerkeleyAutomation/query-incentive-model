from django.db import models

class Person(models.Model):
	email = models.CharField(max_length=256)
	parent = models.CharField(max_length=256)
	parent_node = models.ForeignKey('self', null=True, blank=True, default = None)
	influence = models.FloatField()
	hash = models.CharField(max_length=1024)
	ipaddress = models.CharField(max_length=256)
	session_key = models.CharField(max_length=256)
	created = models.DateTimeField(auto_now = True)
	def __unicode__(self):
		return 'Participant ' + str(self.id)
	class Meta:
		app_label = 'prop30'
		ordering = ['-influence','created']

class Rating(models.Model):
	person = models.ForeignKey(Person, db_index = True, blank = True, null = True)
	rating = models.CharField(max_length=256)
	session_key = models.CharField(max_length=256)
	created = models.DateTimeField(auto_now = True)
	class Meta:
		app_label = 'prop30'

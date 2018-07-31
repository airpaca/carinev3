from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import *

class DomaineFineSerializer(serializers.ModelSerializer):
	class Meta:
		model = DomaineFine
		fields = ('id','libCourt')
		
class DatePrevSerializer(serializers.ModelSerializer):
	class Meta:
		model = DatePrev
		fields = ('id','date_prev','date_prev_to_human','commentaire','previsionniste')
		

		
# class CapteurSerializer(serializers.ModelSerializer):
	# class Meta:
		# model = Capteur
		# fields = ('id','id_capteur_constructeur')
	
# class DicoTypeCapteurSerializer(serializers.ModelSerializer):
	# capteurs = CapteurSerializer(many=True, read_only=True)
	# class Meta:
		# model = DicoTypeCapteur
		# fields = ('id','nom_type_capteur','capteurs')
		

# class MesureSerializer(serializers.ModelSerializer):
	# class Meta:
		# model = Mesure
		# fields = ('id','date_mesure','position','valeur')	
# class StreamSerializer(serializers.ModelSerializer):
	 #mesures = MesureSerializer(many=True, read_only=True)
	# class Meta:
		# model = Stream
		# fields = ('id',)		
# class SessionSerializer(serializers.ModelSerializer):
	# class Meta:
		# model = Session
		# fields = ('id','date_deb','date_fin')
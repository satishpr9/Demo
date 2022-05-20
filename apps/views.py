from email.mime import image
import json
from django.shortcuts import get_object_or_404, render
from rest_framework import generics, permissions
from rest_framework.response import Response
from knox.models import AuthToken
from rest_framework.generics import ListAPIView
from apps.models import Item,file
from .serializers import ItemSerializer, UserSerializer, RegisterSerializer,FileSerializer
from django.contrib.auth import login
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView
from rest_framework.decorators import api_view
from rest_framework import status
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest

from apps import serializers
# Register API
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
        "user": UserSerializer(user, context=self.get_serializer_context()).data,
        "token": AuthToken.objects.create(user)[1]
        })



class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginAPI, self).post(request, format=None)




@api_view(['POST'])
def create_items(request):
    item = ItemSerializer(data=request.data)
    if Item.objects.filter(**request.data).exists():
        raise serializers.ValidationError(' already exists')
  
    if item.is_valid():
        item.save()
        return Response(item.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def all_items(request):
    if request.query_params:
        items = Item.objects.filter(**request.query_param.dict())
    else:
        items = Item.objects.all()
    if items:
        data = ItemSerializer(items)
        return Response(data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
def update_items(request, pk):
    item = Item.objects.get(pk=pk)
    data = ItemSerializer(instance=item, data=request.data)
  
    if data.is_valid():
        data.save()
        return Response(data.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def delete_items(request, pk):
    item = get_object_or_404(Item, pk=pk)
    item.delete()
    return Response(status=status.HTTP_202_ACCEPTED)


@api_view(['POST'])
def uploadImage(request):
    data = request.data

    obj_id = data['obj_id']
    obj= file.objects.get(id=obj_id)

    obj.image = request.FILES.get('image')
    obj.save()

    return Response('Image was uploaded')    


# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
	auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))


def homepage(request):
	currency = 'INR'
	amount = 10000 # Rs. 100

	
	razorpay_order = razorpay_client.order.create(dict(amount=amount,
													currency=currency,
													payment_capture='0'))

	
	razorpay_order_id = razorpay_order['id']
	callback_url = 'paymenthandler/'


	context = {}
	context['razorpay_order_id'] = razorpay_order_id
	context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
	context['razorpay_amount'] = amount
	context['currency'] = currency
	context['callback_url'] = callback_url

	return render(request, 'index.html', context=context)



@csrf_exempt
def paymenthandler(request):

	
	if request.method == "POST":
		try:
		
			
			payment_id = request.POST.get('razorpay_payment_id', '')
			razorpay_order_id = request.POST.get('razorpay_order_id', '')
			signature = request.POST.get('razorpay_signature', '')
			params_dict = {
				'razorpay_order_id': razorpay_order_id,
				'razorpay_payment_id': payment_id,
				'razorpay_signature': signature
			}

			
			result = razorpay_client.utility.verify_payment_signature(
				params_dict)
			if result is None:
				amount = 10000 
				try:

					
					razorpay_client.payment.capture(payment_id, amount)

					
					return render(request, 'success.html')
				except:

					
					return render(request, 'fail.html')
			else:

			
				return render(request, 'fail.html')
		except:

			
			return HttpResponseBadRequest()
	else:
	
		return HttpResponseBadRequest()

from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
import pytest


@pytest.fixture
def authenticate(api_client):
    def do_authenticate(userObject):
        return api_client.force_authenticate(user=userObject)
    return do_authenticate

@pytest.fixture
def create_collection(api_client):
    def do_create_collection(collection):
        return api_client.post('http://127.0.0.1:8000/store/collections/',collection)
    return do_create_collection

@pytest.mark.django_db
class TestCreateCollection:
    #@pytest.mark.skip
    def test_if_user_is_anonymous_return_401(self, create_collection):
        #Arrange- nothing here
        #Act

        response=create_collection({'title':'a'})

        #Assert
        assert response.status_code==status.HTTP_401_UNAUTHORIZED


    def test_if_user_is_not_admin_return_403(self, authenticate, create_collection):
        #Arrange- nothing here
        #Act

        authenticate({})
        response=create_collection({'title':'a'})

        #Assert
        assert response.status_code==status.HTTP_403_FORBIDDEN


    def test_if_data_is_invalid_return_400(self,authenticate, create_collection):
        #Arrange- nothing here
        #Act

        authenticate(User(is_staff=True))
        response=create_collection({'title':''})

        #Assert
        assert response.status_code==status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None


    def test_if_data_is_valid_return_201(self,authenticate, create_collection):
        #Arrange- nothing here
        #Act

        authenticate(User(is_staff=True))
        response=create_collection({'title':'a'})

        #Assert
        assert response.status_code==status.HTTP_201_CREATED
        assert response.data['id']>0
        
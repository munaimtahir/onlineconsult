from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from .models import Department, User, Patient, ConsultRequest


class AuthenticationTestCase(APITestCase):
    """Test authentication endpoints"""
    
    def setUp(self):
        self.department = Department.objects.create(name='Medicine', code='MED')
        self.user = User.objects.create_user(
            username='testdoctor',
            password='testpass123',
            full_name='Dr. Test',
            department=self.department,
            role='doctor'
        )
    
    def test_login_success(self):
        """Test successful login"""
        url = reverse('token_obtain_pair')
        data = {'username': 'testdoctor', 'password': 'testpass123'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_failure(self):
        """Test login with wrong credentials"""
        url = reverse('token_obtain_pair')
        data = {'username': 'testdoctor', 'password': 'wrongpass'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ConsultRequestTestCase(APITestCase):
    """Test consultation request endpoints"""
    
    def setUp(self):
        # Create departments
        self.medicine_dept = Department.objects.create(name='Medicine', code='MED')
        self.cardio_dept = Department.objects.create(name='Cardiology', code='CARD')
        
        # Create users
        self.medicine_doctor = User.objects.create_user(
            username='medic_doc',
            password='testpass123',
            full_name='Dr. Medicine',
            department=self.medicine_dept,
            role='doctor'
        )
        
        self.cardio_doctor = User.objects.create_user(
            username='cardio_doc',
            password='testpass123',
            full_name='Dr. Cardio',
            department=self.cardio_dept,
            role='doctor'
        )
        
        # Create patient
        self.patient = Patient.objects.create(
            hospital_id='TEST001',
            name='Test Patient',
            age=45,
            gender='M'
        )
        
        # Setup API client with authentication
        self.client = APIClient()
        self.client.force_authenticate(user=self.medicine_doctor)
    
    def test_create_consult(self):
        """Test creating a consultation request"""
        url = reverse('consult-list')
        data = {
            'patient': self.patient.id,
            'to_department': self.cardio_dept.id,
            'priority': 'urgent',
            'clinical_summary': 'Patient with chest pain',
            'consult_question': 'Please evaluate for ACS'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ConsultRequest.objects.count(), 1)
        consult = ConsultRequest.objects.first()
        self.assertEqual(consult.patient, self.patient)
        self.assertEqual(consult.from_department, self.medicine_dept)
        self.assertEqual(consult.to_department, self.cardio_dept)
        self.assertEqual(consult.requested_by, self.medicine_doctor)
    
    def test_incoming_consults_filter(self):
        """Test filtering incoming consults"""
        # Create a consult from medicine to cardiology
        ConsultRequest.objects.create(
            patient=self.patient,
            from_department=self.medicine_dept,
            to_department=self.cardio_dept,
            requested_by=self.medicine_doctor,
            priority='routine',
            clinical_summary='Test',
            consult_question='Test question'
        )
        
        # Login as cardio doctor
        self.client.force_authenticate(user=self.cardio_doctor)
        
        # Get incoming consults for cardiology
        url = reverse('consult-list')
        response = self.client.get(url, {'role': 'incoming'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_outgoing_consults_filter(self):
        """Test filtering outgoing consults"""
        # Create a consult from medicine to cardiology
        ConsultRequest.objects.create(
            patient=self.patient,
            from_department=self.medicine_dept,
            to_department=self.cardio_dept,
            requested_by=self.medicine_doctor,
            priority='routine',
            clinical_summary='Test',
            consult_question='Test question'
        )
        
        # Get outgoing consults for medicine (current user)
        url = reverse('consult-list')
        response = self.client.get(url, {'role': 'outgoing'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

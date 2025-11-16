from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Department, User, Patient, ConsultRequest, ConsultComment
from .serializers import (
    DepartmentSerializer, UserSerializer, PatientSerializer,
    ConsultRequestSerializer, ConsultCommentSerializer
)

User = get_user_model()


class DepartmentModelTestCase(TestCase):
    """Test Department model"""
    
    def test_create_department(self):
        """Test creating a department"""
        dept = Department.objects.create(name='Medicine', code='MED')
        self.assertEqual(dept.name, 'Medicine')
        self.assertEqual(dept.code, 'MED')
        self.assertEqual(str(dept), 'Medicine')
    
    def test_department_unique_name(self):
        """Test department name uniqueness"""
        Department.objects.create(name='Medicine', code='MED')
        with self.assertRaises(Exception):
            Department.objects.create(name='Medicine', code='MED2')
    
    def test_department_ordering(self):
        """Test departments are ordered by name"""
        Department.objects.create(name='Surgery', code='SURG')
        Department.objects.create(name='Medicine', code='MED')
        Department.objects.create(name='Cardiology', code='CARD')
        
        depts = list(Department.objects.all())
        self.assertEqual(depts[0].name, 'Cardiology')
        self.assertEqual(depts[1].name, 'Medicine')
        self.assertEqual(depts[2].name, 'Surgery')


class UserModelTestCase(TestCase):
    """Test User model"""
    
    def setUp(self):
        self.department = Department.objects.create(name='Medicine', code='MED')
    
    def test_create_user(self):
        """Test creating a user"""
        user = User.objects.create_user(
            username='testdoc',
            password='pass123',
            full_name='Dr. Test',
            department=self.department,
            role='doctor'
        )
        self.assertEqual(user.username, 'testdoc')
        self.assertEqual(user.full_name, 'Dr. Test')
        self.assertEqual(user.department, self.department)
        self.assertEqual(user.role, 'doctor')
        self.assertTrue(user.check_password('pass123'))
    
    def test_user_string_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(
            username='testdoc',
            password='pass123',
            full_name='Dr. Test',
            department=self.department
        )
        self.assertIn('Dr. Test', str(user))
        self.assertIn('Medicine', str(user))


class PatientModelTestCase(TestCase):
    """Test Patient model"""
    
    def test_create_patient(self):
        """Test creating a patient"""
        patient = Patient.objects.create(
            hospital_id='MRN001',
            name='John Doe',
            age=45,
            gender='M',
            bed_ward_info='Ward A, Bed 1'
        )
        self.assertEqual(patient.hospital_id, 'MRN001')
        self.assertEqual(patient.name, 'John Doe')
        self.assertEqual(patient.age, 45)
        self.assertEqual(patient.gender, 'M')
        self.assertEqual(str(patient), 'John Doe (MRN001)')
    
    def test_patient_unique_hospital_id(self):
        """Test patient hospital_id uniqueness"""
        Patient.objects.create(hospital_id='MRN001', name='John', age=45, gender='M')
        with self.assertRaises(Exception):
            Patient.objects.create(hospital_id='MRN001', name='Jane', age=30, gender='F')
    
    def test_patient_ordering(self):
        """Test patients are ordered by created_at descending"""
        p1 = Patient.objects.create(hospital_id='MRN001', name='John', age=45, gender='M')
        p2 = Patient.objects.create(hospital_id='MRN002', name='Jane', age=30, gender='F')
        
        patients = list(Patient.objects.all())
        self.assertEqual(patients[0], p2)
        self.assertEqual(patients[1], p1)


class ConsultRequestModelTestCase(TestCase):
    """Test ConsultRequest model"""
    
    def setUp(self):
        self.med_dept = Department.objects.create(name='Medicine', code='MED')
        self.card_dept = Department.objects.create(name='Cardiology', code='CARD')
        self.doctor = User.objects.create_user(
            username='doc1',
            password='pass',
            department=self.med_dept
        )
        self.patient = Patient.objects.create(
            hospital_id='MRN001',
            name='John Doe',
            age=45,
            gender='M'
        )
    
    def test_create_consult_request(self):
        """Test creating a consultation request"""
        consult = ConsultRequest.objects.create(
            patient=self.patient,
            from_department=self.med_dept,
            to_department=self.card_dept,
            requested_by=self.doctor,
            priority='urgent',
            status='pending',
            clinical_summary='Patient with chest pain',
            consult_question='Evaluate for ACS'
        )
        self.assertEqual(consult.patient, self.patient)
        self.assertEqual(consult.priority, 'urgent')
        self.assertEqual(consult.status, 'pending')
        self.assertIn('John Doe', str(consult))
    
    def test_consult_default_values(self):
        """Test consultation default values"""
        consult = ConsultRequest.objects.create(
            patient=self.patient,
            from_department=self.med_dept,
            to_department=self.card_dept,
            requested_by=self.doctor,
            clinical_summary='Test',
            consult_question='Test'
        )
        self.assertEqual(consult.priority, 'routine')
        self.assertEqual(consult.status, 'pending')


class ConsultCommentModelTestCase(TestCase):
    """Test ConsultComment model"""
    
    def setUp(self):
        self.med_dept = Department.objects.create(name='Medicine', code='MED')
        self.card_dept = Department.objects.create(name='Cardiology', code='CARD')
        self.doctor = User.objects.create_user(
            username='doc1',
            password='pass',
            department=self.med_dept
        )
        self.patient = Patient.objects.create(
            hospital_id='MRN001',
            name='John Doe',
            age=45,
            gender='M'
        )
        self.consult = ConsultRequest.objects.create(
            patient=self.patient,
            from_department=self.med_dept,
            to_department=self.card_dept,
            requested_by=self.doctor,
            clinical_summary='Test',
            consult_question='Test'
        )
    
    def test_create_comment(self):
        """Test creating a comment"""
        comment = ConsultComment.objects.create(
            consult=self.consult,
            author=self.doctor,
            message='Test comment'
        )
        self.assertEqual(comment.message, 'Test comment')
        self.assertEqual(comment.author, self.doctor)
        self.assertEqual(comment.consult, self.consult)
    
    def test_comment_ordering(self):
        """Test comments are ordered by created_at ascending"""
        c1 = ConsultComment.objects.create(
            consult=self.consult,
            author=self.doctor,
            message='First'
        )
        c2 = ConsultComment.objects.create(
            consult=self.consult,
            author=self.doctor,
            message='Second'
        )
        
        comments = list(ConsultComment.objects.all())
        self.assertEqual(comments[0], c1)
        self.assertEqual(comments[1], c2)


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
    
    def test_token_refresh(self):
        """Test token refresh"""
        # Get tokens
        url = reverse('token_obtain_pair')
        data = {'username': 'testdoctor', 'password': 'testpass123'}
        response = self.client.post(url, data, format='json')
        refresh_token = response.data['refresh']
        
        # Refresh token
        url = reverse('token_refresh')
        data = {'refresh': refresh_token}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class DepartmentAPITestCase(APITestCase):
    """Test Department API endpoints"""
    
    def setUp(self):
        self.department = Department.objects.create(name='Medicine', code='MED')
        self.user = User.objects.create_user(
            username='testdoc',
            password='pass',
            department=self.department
        )
        self.client.force_authenticate(user=self.user)
    
    def test_list_departments(self):
        """Test listing departments"""
        Department.objects.create(name='Surgery', code='SURG')
        Department.objects.create(name='Cardiology', code='CARD')
        
        url = reverse('department-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
    
    def test_get_department_detail(self):
        """Test getting department detail"""
        url = reverse('department-detail', kwargs={'pk': self.department.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Medicine')
    
    def test_unauthenticated_access_denied(self):
        """Test unauthenticated access is denied"""
        self.client.logout()
        url = reverse('department-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PatientAPITestCase(APITestCase):
    """Test Patient API endpoints"""
    
    def setUp(self):
        self.department = Department.objects.create(name='Medicine', code='MED')
        self.user = User.objects.create_user(
            username='testdoc',
            password='pass',
            department=self.department
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_patient(self):
        """Test creating a patient"""
        url = reverse('patient-list')
        data = {
            'hospital_id': 'MRN001',
            'name': 'John Doe',
            'age': 45,
            'gender': 'M',
            'bed_ward_info': 'Ward A'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Patient.objects.count(), 1)
        self.assertEqual(Patient.objects.first().name, 'John Doe')
    
    def test_list_patients(self):
        """Test listing patients"""
        Patient.objects.create(hospital_id='MRN001', name='John', age=45, gender='M')
        Patient.objects.create(hospital_id='MRN002', name='Jane', age=30, gender='F')
        
        url = reverse('patient-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_search_patients(self):
        """Test searching patients"""
        Patient.objects.create(hospital_id='MRN001', name='John Doe', age=45, gender='M')
        Patient.objects.create(hospital_id='MRN002', name='Jane Smith', age=30, gender='F')
        
        url = reverse('patient-list')
        response = self.client.get(url, {'search': 'John'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'John Doe')
    
    def test_get_patient_detail(self):
        """Test getting patient detail"""
        patient = Patient.objects.create(
            hospital_id='MRN001',
            name='John Doe',
            age=45,
            gender='M'
        )
        
        url = reverse('patient-detail', kwargs={'pk': patient.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'John Doe')


class ConsultRequestAPITestCase(APITestCase):
    """Test consultation request endpoints"""
    
    def setUp(self):
        # Create departments
        self.medicine_dept = Department.objects.create(name='Medicine', code='MED')
        self.cardio_dept = Department.objects.create(name='Cardiology', code='CARD')
        self.surgery_dept = Department.objects.create(name='Surgery', code='SURG')
        
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
    
    def test_create_consult_with_inline_patient(self):
        """Test creating a consult with inline patient creation"""
        url = reverse('consult-list')
        data = {
            'patient_data': {
                'hospital_id': 'MRN999',
                'name': 'New Patient',
                'age': 50,
                'gender': 'F'
            },
            'to_department': self.cardio_dept.id,
            'priority': 'routine',
            'clinical_summary': 'Test summary',
            'consult_question': 'Test question'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Patient.objects.count(), 2)
        self.assertEqual(Patient.objects.filter(hospital_id='MRN999').count(), 1)
    
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
    
    def test_consult_status_filter(self):
        """Test filtering consults by status"""
        ConsultRequest.objects.create(
            patient=self.patient,
            from_department=self.medicine_dept,
            to_department=self.cardio_dept,
            requested_by=self.medicine_doctor,
            status='pending',
            clinical_summary='Test',
            consult_question='Test'
        )
        ConsultRequest.objects.create(
            patient=self.patient,
            from_department=self.medicine_dept,
            to_department=self.surgery_dept,
            requested_by=self.medicine_doctor,
            status='completed',
            clinical_summary='Test',
            consult_question='Test'
        )
        
        url = reverse('consult-list')
        response = self.client.get(url, {'status': 'pending'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_consult_detail(self):
        """Test getting consultation detail"""
        consult = ConsultRequest.objects.create(
            patient=self.patient,
            from_department=self.medicine_dept,
            to_department=self.cardio_dept,
            requested_by=self.medicine_doctor,
            clinical_summary='Test summary',
            consult_question='Test question'
        )
        
        url = reverse('consult-detail', kwargs={'pk': consult.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], consult.id)
        self.assertIn('patient_details', response.data)
        self.assertIn('comments', response.data)
    
    def test_add_comment_to_consult(self):
        """Test adding a comment to a consultation"""
        consult = ConsultRequest.objects.create(
            patient=self.patient,
            from_department=self.medicine_dept,
            to_department=self.cardio_dept,
            requested_by=self.medicine_doctor,
            clinical_summary='Test',
            consult_question='Test'
        )
        
        url = reverse('consult-add-comment', kwargs={'pk': consult.id})
        data = {'message': 'Test comment'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ConsultComment.objects.count(), 1)
        self.assertEqual(ConsultComment.objects.first().message, 'Test comment')
    
    def test_add_comment_without_message(self):
        """Test adding a comment without message fails"""
        consult = ConsultRequest.objects.create(
            patient=self.patient,
            from_department=self.medicine_dept,
            to_department=self.cardio_dept,
            requested_by=self.medicine_doctor,
            clinical_summary='Test',
            consult_question='Test'
        )
        
        url = reverse('consult-add-comment', kwargs={'pk': consult.id})
        data = {'message': ''}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_consult_comments(self):
        """Test getting consultation comments"""
        consult = ConsultRequest.objects.create(
            patient=self.patient,
            from_department=self.medicine_dept,
            to_department=self.cardio_dept,
            requested_by=self.medicine_doctor,
            clinical_summary='Test',
            consult_question='Test'
        )
        
        ConsultComment.objects.create(
            consult=consult,
            author=self.medicine_doctor,
            message='First comment'
        )
        ConsultComment.objects.create(
            consult=consult,
            author=self.cardio_doctor,
            message='Second comment'
        )
        
        url = reverse('consult-comments', kwargs={'pk': consult.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_update_consult_status(self):
        """Test updating consultation status"""
        consult = ConsultRequest.objects.create(
            patient=self.patient,
            from_department=self.medicine_dept,
            to_department=self.cardio_dept,
            requested_by=self.medicine_doctor,
            status='pending',
            clinical_summary='Test',
            consult_question='Test'
        )
        
        url = reverse('consult-update-status', kwargs={'pk': consult.id})
        data = {'status': 'in_progress'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        consult.refresh_from_db()
        self.assertEqual(consult.status, 'in_progress')
    
    def test_update_consult_status_invalid(self):
        """Test updating consultation status with invalid value"""
        consult = ConsultRequest.objects.create(
            patient=self.patient,
            from_department=self.medicine_dept,
            to_department=self.cardio_dept,
            requested_by=self.medicine_doctor,
            clinical_summary='Test',
            consult_question='Test'
        )
        
        url = reverse('consult-update-status', kwargs={'pk': consult.id})
        data = {'status': 'invalid_status'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_search_consults(self):
        """Test searching consultations"""
        patient1 = Patient.objects.create(
            hospital_id='MRN001',
            name='John Doe',
            age=45,
            gender='M'
        )
        patient2 = Patient.objects.create(
            hospital_id='MRN002',
            name='Jane Smith',
            age=30,
            gender='F'
        )
        
        ConsultRequest.objects.create(
            patient=patient1,
            from_department=self.medicine_dept,
            to_department=self.cardio_dept,
            requested_by=self.medicine_doctor,
            clinical_summary='Test',
            consult_question='Test'
        )
        ConsultRequest.objects.create(
            patient=patient2,
            from_department=self.medicine_dept,
            to_department=self.cardio_dept,
            requested_by=self.medicine_doctor,
            clinical_summary='Test',
            consult_question='Test'
        )
        
        url = reverse('consult-list')
        response = self.client.get(url, {'search': 'John'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class SerializerTestCase(TestCase):
    """Test serializers"""
    
    def setUp(self):
        self.department = Department.objects.create(name='Medicine', code='MED')
        self.user = User.objects.create_user(
            username='testdoc',
            password='pass',
            full_name='Dr. Test',
            department=self.department
        )
        self.patient = Patient.objects.create(
            hospital_id='MRN001',
            name='John Doe',
            age=45,
            gender='M'
        )
    
    def test_department_serializer(self):
        """Test DepartmentSerializer"""
        serializer = DepartmentSerializer(self.department)
        self.assertEqual(serializer.data['name'], 'Medicine')
        self.assertEqual(serializer.data['code'], 'MED')
    
    def test_user_serializer(self):
        """Test UserSerializer"""
        serializer = UserSerializer(self.user)
        self.assertEqual(serializer.data['username'], 'testdoc')
        self.assertEqual(serializer.data['full_name'], 'Dr. Test')
        self.assertEqual(serializer.data['department_name'], 'Medicine')
    
    def test_patient_serializer(self):
        """Test PatientSerializer"""
        serializer = PatientSerializer(self.patient)
        self.assertEqual(serializer.data['hospital_id'], 'MRN001')
        self.assertEqual(serializer.data['name'], 'John Doe')
        self.assertEqual(serializer.data['age'], 45)
    
    def test_consult_comment_serializer(self):
        """Test ConsultCommentSerializer"""
        card_dept = Department.objects.create(name='Cardiology', code='CARD')
        consult = ConsultRequest.objects.create(
            patient=self.patient,
            from_department=self.department,
            to_department=card_dept,
            requested_by=self.user,
            clinical_summary='Test',
            consult_question='Test'
        )
        comment = ConsultComment.objects.create(
            consult=consult,
            author=self.user,
            message='Test message'
        )
        
        serializer = ConsultCommentSerializer(comment)
        self.assertEqual(serializer.data['message'], 'Test message')
        self.assertEqual(serializer.data['author_name'], 'Dr. Test')
        self.assertEqual(serializer.data['author_username'], 'testdoc')


class ConsultRequestCreateSerializerTestCase(APITestCase):
    """Test ConsultRequestCreateSerializer validation"""
    
    def setUp(self):
        self.med_dept = Department.objects.create(name='Medicine', code='MED')
        self.card_dept = Department.objects.create(name='Cardiology', code='CARD')
        self.doctor = User.objects.create_user(
            username='doc1',
            password='pass',
            department=self.med_dept
        )
        self.client.force_authenticate(user=self.doctor)
    
    def test_create_consult_without_patient_or_patient_data(self):
        """Test that creating consult without patient or patient_data fails"""
        url = reverse('consult-list')
        data = {
            'to_department': self.card_dept.id,
            'priority': 'routine',
            'clinical_summary': 'Test summary',
            'consult_question': 'Test question'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('patient', str(response.data).lower() or 'patient_data' in str(response.data).lower())


class SeedDataCommandTestCase(TestCase):
    """Test seed_data management command"""
    
    def test_seed_data_command(self):
        """Test that seed_data command creates initial data"""
        from django.core.management import call_command
        from io import StringIO
        
        # Run the command
        out = StringIO()
        call_command('seed_data', stdout=out)
        
        # Check that departments were created
        self.assertEqual(Department.objects.count(), 5)
        self.assertTrue(Department.objects.filter(name='Medicine').exists())
        self.assertTrue(Department.objects.filter(name='Surgery').exists())
        self.assertTrue(Department.objects.filter(name='Cardiology').exists())
        
        # Check that users were created
        self.assertTrue(User.objects.filter(username='admin').exists())
        self.assertTrue(User.objects.filter(username='doctor_medicine').exists())
        self.assertTrue(User.objects.filter(username='doctor_surgery').exists())
        
        # Check that admin has correct permissions
        admin = User.objects.get(username='admin')
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        
        # Check that patients were created
        self.assertGreaterEqual(Patient.objects.count(), 3)
        
        # Check that sample consults were created
        self.assertGreaterEqual(ConsultRequest.objects.count(), 2)
    
    def test_seed_data_idempotent(self):
        """Test that running seed_data twice doesn't create duplicates"""
        from django.core.management import call_command
        from io import StringIO
        
        # Run the command twice
        out = StringIO()
        call_command('seed_data', stdout=out)
        
        dept_count = Department.objects.count()
        user_count = User.objects.count()
        
        # Run again
        out = StringIO()
        call_command('seed_data', stdout=out)
        
        # Counts should be the same
        self.assertEqual(Department.objects.count(), dept_count)
        self.assertEqual(User.objects.count(), user_count)


class AdminTestCase(TestCase):
    """Test admin interface"""
    
    def setUp(self):
        self.department = Department.objects.create(name='Medicine', code='MED')
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@test.com',
            department=self.department
        )
    
    def test_admin_site_accessible(self):
        """Test that admin site is accessible"""
        from django.contrib import admin
        from consults.admin import DepartmentAdmin, UserAdmin, PatientAdmin, ConsultRequestAdmin, ConsultCommentAdmin
        
        # Check that models are registered
        self.assertIn(Department, admin.site._registry)
        self.assertIn(User, admin.site._registry)
        self.assertIn(Patient, admin.site._registry)
        self.assertIn(ConsultRequest, admin.site._registry)
        self.assertIn(ConsultComment, admin.site._registry)


class EdgeCaseTestCase(APITestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        self.med_dept = Department.objects.create(name='Medicine', code='MED')
        self.card_dept = Department.objects.create(name='Cardiology', code='CARD')
        self.doctor = User.objects.create_user(
            username='doc1',
            password='pass',
            department=self.med_dept
        )
        self.patient = Patient.objects.create(
            hospital_id='MRN001',
            name='John Doe',
            age=45,
            gender='M'
        )
        self.client.force_authenticate(user=self.doctor)
    
    def test_update_nonexistent_consult_status(self):
        """Test updating status of non-existent consult"""
        url = reverse('consult-update-status', kwargs={'pk': 9999})
        data = {'status': 'in_progress'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_add_comment_to_nonexistent_consult(self):
        """Test adding comment to non-existent consult"""
        url = reverse('consult-add-comment', kwargs={'pk': 9999})
        data = {'message': 'Test comment'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_nonexistent_patient(self):
        """Test getting non-existent patient"""
        url = reverse('patient-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_nonexistent_department(self):
        """Test getting non-existent department"""
        url = reverse('department-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_partial_update_consult(self):
        """Test partial update of consult"""
        consult = ConsultRequest.objects.create(
            patient=self.patient,
            from_department=self.med_dept,
            to_department=self.card_dept,
            requested_by=self.doctor,
            priority='routine',
            clinical_summary='Original summary',
            consult_question='Original question'
        )
        
        url = reverse('consult-detail', kwargs={'pk': consult.id})
        data = {'priority': 'urgent'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        consult.refresh_from_db()
        self.assertEqual(consult.priority, 'urgent')
        self.assertEqual(consult.clinical_summary, 'Original summary')

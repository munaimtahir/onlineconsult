from django.core.management.base import BaseCommand
from consults.models import Department, User, Patient, ConsultRequest, ConsultComment


class Command(BaseCommand):
    help = 'Seeds the database with initial data for departments, users, and sample patients'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting data seeding...')
        
        # Create Departments
        departments_data = [
            {'name': 'Medicine', 'code': 'MED'},
            {'name': 'Surgery', 'code': 'SURG'},
            {'name': 'Cardiology', 'code': 'CARD'},
            {'name': 'Radiology', 'code': 'RAD'},
            {'name': 'Pathology', 'code': 'PATH'},
        ]
        
        departments = {}
        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={'code': dept_data['code']}
            )
            departments[dept_data['name']] = dept
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  {status}: Department {dept.name}')
        
        # Create Admin User
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'full_name': 'System Administrator',
                'email': 'admin@hospital.com',
                'is_staff': True,
                'is_superuser': True,
                'role': 'admin',
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(f'  Created: Admin user (username: admin, password: admin123)')
        else:
            self.stdout.write(f'  Already exists: Admin user')
        
        # Create Doctor Users
        doctors_data = [
            {
                'username': 'doctor_medicine',
                'full_name': 'Dr. John Smith',
                'email': 'john.smith@hospital.com',
                'department': 'Medicine',
                'password': 'doctor123'
            },
            {
                'username': 'doctor_surgery',
                'full_name': 'Dr. Sarah Johnson',
                'email': 'sarah.johnson@hospital.com',
                'department': 'Surgery',
                'password': 'doctor123'
            },
            {
                'username': 'doctor_cardiology',
                'full_name': 'Dr. Michael Brown',
                'email': 'michael.brown@hospital.com',
                'department': 'Cardiology',
                'password': 'doctor123'
            },
            {
                'username': 'doctor_radiology',
                'full_name': 'Dr. Emily Davis',
                'email': 'emily.davis@hospital.com',
                'department': 'Radiology',
                'password': 'doctor123'
            },
            {
                'username': 'doctor_pathology',
                'full_name': 'Dr. Robert Wilson',
                'email': 'robert.wilson@hospital.com',
                'department': 'Pathology',
                'password': 'doctor123'
            },
        ]
        
        for doc_data in doctors_data:
            password = doc_data.pop('password')
            dept_name = doc_data.pop('department')
            
            doctor, created = User.objects.get_or_create(
                username=doc_data['username'],
                defaults={
                    **doc_data,
                    'department': departments[dept_name],
                    'role': 'doctor',
                }
            )
            if created:
                doctor.set_password(password)
                doctor.save()
                self.stdout.write(f'  Created: {doctor.full_name} ({doctor.username}) - {dept_name}')
            else:
                self.stdout.write(f'  Already exists: {doctor.full_name}')
        
        # Create Sample Patients
        patients_data = [
            {
                'hospital_id': 'MRN001',
                'name': 'Alice Anderson',
                'age': 45,
                'gender': 'F',
                'bed_ward_info': 'Ward A, Bed 12'
            },
            {
                'hospital_id': 'MRN002',
                'name': 'Bob Builder',
                'age': 62,
                'gender': 'M',
                'bed_ward_info': 'Ward B, Bed 5'
            },
            {
                'hospital_id': 'MRN003',
                'name': 'Carol Carter',
                'age': 38,
                'gender': 'F',
                'bed_ward_info': 'ICU Bed 3'
            },
        ]
        
        for patient_data in patients_data:
            patient, created = Patient.objects.get_or_create(
                hospital_id=patient_data['hospital_id'],
                defaults=patient_data
            )
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  {status}: Patient {patient.name} ({patient.hospital_id})')
        
        # Create Sample Consult Requests
        try:
            medicine_doc = User.objects.get(username='doctor_medicine')
            patient1 = Patient.objects.get(hospital_id='MRN001')
            patient2 = Patient.objects.get(hospital_id='MRN002')
            
            consult1, created = ConsultRequest.objects.get_or_create(
                patient=patient1,
                from_department=departments['Medicine'],
                to_department=departments['Cardiology'],
                defaults={
                    'requested_by': medicine_doc,
                    'priority': 'urgent',
                    'status': 'pending',
                    'clinical_summary': 'Patient with chest pain, elevated troponin levels.',
                    'consult_question': 'Please evaluate for acute coronary syndrome. ECG shows ST elevation in leads II, III, aVF.',
                }
            )
            if created:
                self.stdout.write(f'  Created: Sample consult request for {patient1.name}')
            
            consult2, created = ConsultRequest.objects.get_or_create(
                patient=patient2,
                from_department=departments['Medicine'],
                to_department=departments['Surgery'],
                defaults={
                    'requested_by': medicine_doc,
                    'priority': 'routine',
                    'status': 'pending',
                    'clinical_summary': 'Patient with recurrent abdominal pain, suspected cholecystitis.',
                    'consult_question': 'Please evaluate for possible cholecystectomy. Ultrasound shows gallstones.',
                }
            )
            if created:
                self.stdout.write(f'  Created: Sample consult request for {patient2.name}')
                
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  Could not create sample consults: {e}'))
        
        self.stdout.write(self.style.SUCCESS('Data seeding completed successfully!'))
        self.stdout.write('')
        self.stdout.write('Default credentials:')
        self.stdout.write('  Admin: username=admin, password=admin123')
        self.stdout.write('  Doctors: username=doctor_[department], password=doctor123')
        self.stdout.write('  (e.g., doctor_medicine, doctor_cardiology, etc.)')

from rest_framework import serializers
from .models import Department, User, Patient, ConsultRequest, ConsultComment


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'created_at']
        read_only_fields = ['created_at']


class UserSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'department', 'department_name', 'role']
        read_only_fields = ['id']


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'hospital_id', 'name', 'age', 'gender', 'bed_ward_info', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ConsultCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = ConsultComment
        fields = ['id', 'consult', 'author', 'author_name', 'author_username', 'message', 'created_at']
        read_only_fields = ['created_at', 'author']


class ConsultRequestSerializer(serializers.ModelSerializer):
    patient_details = PatientSerializer(source='patient', read_only=True)
    from_department_name = serializers.CharField(source='from_department.name', read_only=True)
    to_department_name = serializers.CharField(source='to_department.name', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.full_name', read_only=True)
    comments = ConsultCommentSerializer(many=True, read_only=True)
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)
    
    class Meta:
        model = ConsultRequest
        fields = [
            'id', 'patient', 'patient_details', 'from_department', 'from_department_name',
            'to_department', 'to_department_name', 'requested_by', 'requested_by_name',
            'priority', 'status', 'clinical_summary', 'consult_question',
            'created_at', 'updated_at', 'comments', 'comment_count'
        ]
        read_only_fields = ['created_at', 'updated_at', 'requested_by', 'from_department']
    
    def create(self, validated_data):
        # Automatically set from_department and requested_by from current user
        request = self.context.get('request')
        if request and request.user:
            validated_data['requested_by'] = request.user
            validated_data['from_department'] = request.user.department
        return super().create(validated_data)


class ConsultRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating consults with optional inline patient creation"""
    patient_data = PatientSerializer(required=False, write_only=True)
    patient = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = ConsultRequest
        fields = [
            'patient', 'patient_data', 'to_department', 'priority', 
            'clinical_summary', 'consult_question'
        ]
    
    def validate(self, data):
        """Ensure either patient or patient_data is provided"""
        if not data.get('patient') and not data.get('patient_data'):
            raise serializers.ValidationError(
                "Either 'patient' or 'patient_data' must be provided."
            )
        return data
    
    def create(self, validated_data):
        patient_data = validated_data.pop('patient_data', None)
        
        # If patient_data is provided, create new patient
        if patient_data:
            patient = Patient.objects.create(**patient_data)
            validated_data['patient'] = patient
        
        # Set from_department and requested_by from current user
        request = self.context.get('request')
        if request and request.user:
            validated_data['requested_by'] = request.user
            validated_data['from_department'] = request.user.department
        
        return super().create(validated_data)

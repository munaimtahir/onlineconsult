from django.db import models
from django.contrib.auth.models import AbstractUser


class Department(models.Model):
    """Hospital department model"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class User(AbstractUser):
    """Custom user model extending Django's AbstractUser"""
    ROLE_CHOICES = [
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
    ]
    
    full_name = models.CharField(max_length=200, blank=True)
    department = models.ForeignKey(
        Department, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='users'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='doctor')
    
    def __str__(self):
        return f"{self.full_name or self.username} ({self.department})"


class Patient(models.Model):
    """Patient model with minimal information"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    hospital_id = models.CharField(max_length=50, unique=True, help_text="MRN or Hospital ID")
    name = models.CharField(max_length=200)
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    bed_ward_info = models.CharField(max_length=100, blank=True, help_text="Bed/Ward information")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.hospital_id})"


class ConsultRequest(models.Model):
    """Consultation request model"""
    PRIORITY_CHOICES = [
        ('routine', 'Routine'),
        ('urgent', 'Urgent'),
        ('stat', 'STAT/Emergency'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='consults')
    from_department = models.ForeignKey(
        Department, 
        on_delete=models.CASCADE, 
        related_name='outgoing_consults'
    )
    to_department = models.ForeignKey(
        Department, 
        on_delete=models.CASCADE, 
        related_name='incoming_consults'
    )
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_consults')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='routine')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    clinical_summary = models.TextField(help_text="Clinical summary of the patient")
    consult_question = models.TextField(help_text="Specific consultation question")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Consult #{self.id}: {self.patient.name} - {self.from_department} to {self.to_department}"


class ConsultComment(models.Model):
    """Comment/Reply on a consultation request"""
    consult = models.ForeignKey(ConsultRequest, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on Consult #{self.consult.id}"

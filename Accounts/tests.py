# tests/test_models.py
from django.core.files.uploadedfile import File
from django.core.files.uploadedfile import SimpleUploadedFile
from Accounts.views import process_audio, predict_emotion
import json
import os
from django.core import mail
from Accounts.models import Customer
from Accounts.models import Customer, Reviews, Status
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.test import TestCase, Client
from django.test import TestCase
from django.contrib.auth.models import User
from Accounts.models import Customer, Reviews, Status, StaffProfile, Activity
from django.utils import timezone
import uuid  # Added for generating unique tokens


class BaseTestCase(TestCase):
    def tearDown(self):
        print(
            f"✅ {self.__class__.__name__}.{self._testMethodName} completed successfully")
        super().tearDown()


class CustomerModelTest(BaseTestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin', password='password123')
        self.customer = Customer.objects.create(
            customerEmail='test@example.com',
            roomType='double',
            noOfDays=3,
            adminUserID=self.admin_user,
            tokenNumber=f"token_{uuid.uuid4().hex}"  # Unique token
        )

    def test_customer_creation(self):
        """Test the basic creation of a customer"""
        self.assertEqual(self.customer.customerEmail, 'test@example.com')
        self.assertEqual(self.customer.roomType, 'double')
        self.assertEqual(self.customer.noOfDays, 3)
        self.assertEqual(self.customer.activityStatus, 0)
        self.assertFalse(self.customer.email_verified)

    def test_charge_calculation(self):
        """Test that charge is calculated correctly based on room type and days"""
        self.assertEqual(self.customer.charge,
                         6000)  # 3 days * 2000 (double room)

        # Test with different room type - added unique tokenNumber
        customer2 = Customer.objects.create(
            customerEmail='test2@example.com',
            roomType='deluxe',
            noOfDays=2,
            tokenNumber=f"token_{uuid.uuid4().hex}"  # Unique token
        )
        self.assertEqual(customer2.charge, 6000)  # 2 days * 3000 (deluxe room)


class ReviewModelTest(BaseTestCase):
    def setUp(self):
        self.review = Reviews.objects.create(
            review="Great service and friendly staff!",
            emotion="positive",
            email="customer@example.com",
            responseAlert=False
        )

    def test_review_creation(self):
        """Test the basic creation of a review"""
        self.assertEqual(self.review.review,
                         "Great service and friendly staff!")
        self.assertEqual(self.review.emotion, "positive")
        self.assertEqual(self.review.email, "customer@example.com")
        self.assertFalse(self.review.responseAlert)
        self.assertIsNotNone(self.review.created_at)


class StatusModelTest(BaseTestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            customerEmail='test@example.com',
            roomType='single',
            noOfDays=1,
            tokenNumber=f"token_{uuid.uuid4().hex}"  # Unique token
        )
        self.status = Status.objects.create(
            deliveryStatus='delivered',
            isValid=True,
            customerEmail=self.customer
        )

    def test_status_creation(self):
        """Test the basic creation of a status"""
        self.assertEqual(self.status.deliveryStatus, 'delivered')
        self.assertTrue(self.status.isValid)
        self.assertEqual(self.status.customerEmail, self.customer)


# tests/test_views.py


class LoginViewTest(BaseTestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )

    def test_login_page_loads(self):
        """Test that login page loads correctly"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Accounts/login.html')

    def test_login_success(self):
        """Test successful login redirects to dashboard"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_failure(self):
        """Test failed login shows error message"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Please check your username or password again.")


class DashboardViewTest(BaseTestCase):
    def setUp(self):
        self.client = Client()
        self.dashboard_url = reverse('dashboard')

        # Create user and assign to staff group
        self.user = User.objects.create_user(
            username='staffuser',
            password='staffpass'
        )
        self.staff_group = Group.objects.create(name='staff')
        self.user.groups.add(self.staff_group)

        # Create sample reviews
        Reviews.objects.create(
            review="Excellent service",
            emotion="positive",
            email="customer1@example.com"
        )
        Reviews.objects.create(
            review="Room was dirty",
            emotion="negative",
            email="customer2@example.com"
        )
        Reviews.objects.create(
            review="Average experience",
            emotion="neutral",
            email="customer3@example.com"
        )

    def test_dashboard_access_authenticated(self):
        """Test that authenticated staff user can access dashboard"""
        self.client.login(username='staffuser', password='staffpass')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Accounts/dashboard.html')

    def test_dashboard_access_unauthenticated(self):
        """Test that unauthenticated user is redirected to login"""
        response = self.client.get(self.dashboard_url)
        self.assertRedirects(response, f'/login/?next={self.dashboard_url}')

    def test_dashboard_shows_reviews(self):
        """Test that dashboard shows all reviews"""
        self.client.login(username='staffuser', password='staffpass')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['reviews']), 3)

    def test_dashboard_filtering(self):
        """Test that dashboard filters work correctly"""
        self.client.login(username='staffuser', password='staffpass')

        # Filter by emotion
        response = self.client.get(f"{self.dashboard_url}?emotion=positive")
        self.assertEqual(len(response.context['reviews']), 1)
        self.assertEqual(response.context['reviews'][0].emotion, "positive")


class ReviewSubmissionTest(BaseTestCase):
    def setUp(self):
        self.client = Client()
        self.review_url = reverse('give_review')

        # Create verified customer
        self.customer = Customer.objects.create(
            customerEmail='customer@example.com',
            roomType='double',
            noOfDays=2,
            activityStatus=1,
            email_verified=True,
            verified_at=timezone.now(),
            tokenNumber=f"token_{uuid.uuid4().hex}"  # Unique token
        )

    def test_review_form_loads(self):
        """Test that review form loads correctly"""
        response = self.client.get(self.review_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Accounts/give_review.html')

    def test_review_submission_success(self):
        """Test successful review submission"""
        response = self.client.post(self.review_url, {
            'email': 'customer@example.com',
            'review': 'Excellent service and comfortable rooms.',
            'responseAlert': False
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Thank you for your review!")

        # Verify review was saved
        self.assertEqual(Reviews.objects.count(), 1)
        review = Reviews.objects.first()
        self.assertEqual(review.email, 'customer@example.com')
        self.assertEqual(
            review.review, 'Excellent service and comfortable rooms.')

    def test_review_submission_unverified_customer(self):
        """Test review submission from unverified customer"""
        Customer.objects.create(
            customerEmail='unverified@example.com',
            roomType='single',
            noOfDays=1,
            activityStatus=0,
            email_verified=False,
            tokenNumber=f"token_{uuid.uuid4().hex}"  # Unique token
        )

        response = self.client.post(self.review_url, {
            'email': 'unverified@example.com',
            'review': 'Nice hotel.',
            'responseAlert': False
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "This email is not registered or not verified")

        # Verify no review was saved
        self.assertEqual(Reviews.objects.count(), 0)


# tests/test_customer_registration.py


class CustomerRegistrationTest(BaseTestCase):
    def setUp(self):
        self.client = Client()
        self.registration_url = reverse('register_customer')

        # Create staff user
        self.user = User.objects.create_user(
            username='staffuser',
            password='staffpass'
        )
        self.staff_group = Group.objects.create(name='staff')
        self.user.groups.add(self.staff_group)
        self.client.login(username='staffuser', password='staffpass')

    def test_customer_registration_form_loads(self):
        """Test that customer registration form loads correctly"""
        response = self.client.get(self.registration_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'Accounts/customer_registration.html')

    def test_customer_registration_success(self):
        """Test successful customer registration"""
        response = self.client.post(self.registration_url, {
            'customerEmail': 'newcustomer@example.com',
            'roomType': 'deluxe',
            'noOfDays': 3
        })
        self.assertRedirects(response, reverse('dashboard'))

        # Verify customer was created
        self.assertEqual(Customer.objects.count(), 1)
        customer = Customer.objects.first()
        self.assertEqual(customer.customerEmail, 'newcustomer@example.com')
        self.assertEqual(customer.roomType, 'deluxe')
        self.assertEqual(customer.noOfDays, 3)
        self.assertEqual(customer.charge, 9000)  # 3 days * 3000 (deluxe)
        self.assertFalse(customer.email_verified)

        # Verify email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['newcustomer@example.com'])

    def test_customer_verification_process(self):
        """Test customer verification process"""
        # Create customer with verification token
        customer = Customer.objects.create(
            customerEmail='verify@example.com',
            roomType='single',
            noOfDays=1,
            verification_token='abc123xyz',
            email_verified=False,
            tokenNumber=f"token_{uuid.uuid4().hex}"  # Unique token
        )

        # Access verification URL
        verify_url = reverse('verify_customer', args=['abc123xyz'])
        response = self.client.get(verify_url)
        self.assertRedirects(response, reverse('confirmation'))

        # Refresh customer from database
        customer.refresh_from_db()

        # Verify customer was updated
        self.assertTrue(customer.email_verified)
        self.assertIsNotNone(customer.verified_at)
        self.assertEqual(customer.activityStatus, 1)
        self.assertIsNone(customer.verification_token)
        self.assertNotEqual(customer.tokenNumber, '')


# tests/test_integration.py


class CustomerReviewIntegrationTest(BaseTestCase):
    """Integration test for the customer registration, verification, and review submission process"""

    def setUp(self):
        self.client = Client()

        # Create admin user
        self.admin_user = User.objects.create_user(
            username='adminuser',
            password='adminpass'
        )
        self.admin_group = Group.objects.create(name='admin')
        self.admin_user.groups.add(self.admin_group)

        # Create staff user
        self.staff_user = User.objects.create_user(
            username='staffuser',
            password='staffpass'
        )
        self.staff_group = Group.objects.create(name='staff')
        self.staff_user.groups.add(self.staff_group)

    def test_customer_flow(self):

        # Step 1: Staff registers customer
        self.client.login(username='staffuser', password='staffpass')
        registration_response = self.client.post(reverse('register_customer'), {
            'customerEmail': 'customer@example.com',
            'roomType': 'double',
            'noOfDays': 2
        })
        self.assertRedirects(registration_response, reverse('dashboard'))

        # Verify customer created but not verified
        customer = Customer.objects.get(customerEmail='customer@example.com')
        self.assertFalse(customer.email_verified)
        self.assertEqual(customer.activityStatus, 0)

        # Step 2: Extract verification token from customer
        verification_token = customer.verification_token

        # Step 3: Customer uses verification link
        verification_response = self.client.get(
            reverse('verify_customer', args=[verification_token])
        )
        self.assertRedirects(verification_response, reverse('confirmation'))

        # Refresh customer data
        customer.refresh_from_db()
        self.assertTrue(customer.email_verified)
        self.assertEqual(customer.activityStatus, 1)

        # Step 4: Customer submits review
        review_response = self.client.post(reverse('give_review'), {
            'email': 'customer@example.com',
            'review': 'Wonderful hotel with excellent amenities.',
            'responseAlert': True
        })
        self.assertEqual(review_response.status_code, 200)
        self.assertContains(review_response, "Thank you for your review!")

        # Step 5: Admin views review in dashboard
        self.client.logout()
        self.client.login(username='adminuser', password='adminpass')
        dashboard_response = self.client.get(reverse('dashboard'))
        self.assertEqual(dashboard_response.status_code, 200)

        # Check that review is present in dashboard
        self.assertEqual(len(dashboard_response.context['reviews']), 1)
        review = dashboard_response.context['reviews'][0]
        self.assertEqual(review.email, 'customer@example.com')
        self.assertEqual(
            review.review, 'Wonderful hotel with excellent amenities.')
        self.assertTrue(review.responseAlert)

        # Step 6: Admin views customer info
        customer_info_response = self.client.get(reverse('customer_info'))
        self.assertEqual(customer_info_response.status_code, 200)

        # Check that customer is present in customer info
        self.assertEqual(len(customer_info_response.context['customers']), 1)
        customer_info = customer_info_response.context['customers'][0]
        self.assertEqual(customer_info.customerEmail, 'customer@example.com')
        self.assertEqual(customer_info.roomType, 'double')
        self.assertEqual(customer_info.noOfDays, 2)
        self.assertEqual(customer_info.charge, 4000)  # 2 days * 2000 (double)


# Testing text to emotion processing:
class EmotionPredictionTest(TestCase):
    def test_predict_emotion_basic_functionality(self):
        """Simple test to verify the emotion prediction works in the backend flow"""

        # Simple test input
        test_input = "I loved the service and the staff were very friendly."

        # Call the prediction function
        try:
            emotion = predict_emotion(test_input)

            # Check that we got a result
            self.assertIsNotNone(emotion)
            self.assertIsInstance(emotion, str)
            self.assertTrue(len(emotion) > 0,
                            "Emotion prediction should not be empty")

            # Print the result for manual verification
            print(f"\nInput: '{test_input}'")
            print(f"Predicted emotion: {emotion}")

            # Test passed if we reach this point without errors
            print("Emotion prediction is working correctly in the backend flow")
        except Exception as e:
            self.fail(f"Emotion prediction failed with error: {str(e)}")


# Testing audio integration processing:


class WhisperIntegrationTest(BaseTestCase):

    def test_process_audio(self):

        # Path to  test audio file
        audio_file_path = r"D:\crm\media\Recording.wav"

        self.assertTrue(os.path.exists(audio_file_path),
                        f"Test audio file not found: {audio_file_path}")

        # Open the file
        with open(audio_file_path, 'rb') as f:
            # Create a Django File object to mimic what your view would receive
            django_file = File(f, name=os.path.basename(audio_file_path))

            # Process the audio
            transcription = process_audio(django_file)

            # Check if we got a valid transcription
            self.assertIsInstance(transcription, str)
            self.assertTrue(len(transcription) > 0,
                            "Transcription should not be empty if Whisper is working")

            # Print the transcription to verify it looks reasonable
            print(f"\nTranscription result: {transcription}")

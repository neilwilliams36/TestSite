from django.test import TestCase
import datetime
from django.utils import timezone
from django.core.urlresolvers import reverse

from polls.models import Poll

# Create your tests here.
def create_poll(question, days):
    '''Creates a poll with the given question published the number of day offset to now
    (negative for polls published in past, positive for polls that have yet to be published)'''
    return Poll.objects.create(question=question, pub_date=timezone.now() + datetime.timedelta(days=days))
    
    
class PollMethodTests(TestCase):
    
    def test_was_published_recently_with_future_poll(self):
        '''was_published_recently() should return False for polls whose pub_date is in the future'''
        future_poll = Poll(pub_date = timezone.now() + datetime.timedelta(days=30))
        self.assertEqual(future_poll.was_published_recently(), False)
    
    def test_was_published_recently_with_old_poll(self):
        '''waas_published_recently() should return False for polls whose pub_date is older than 1 day'''
        old_poll = Poll(pub_date = timezone.now() - datetime.timedelta(days=30))
        self.assertEqual(old_poll.was_published_recently(), False)
    
    def test_was_published_recently_with_recent_poll(self):
        '''was_published_recently should return True for polls whose pub_date is within the last day'''
        recent_poll = Poll(pub_date = timezone.now()- datetime.timedelta(hours=1))
        self.assertEqual(recent_poll.was_published_recently(), True)

class PollViewTests(TestCase):
    def test_index_view_with_no_polls(self):
        '''If no polls exist, an appropriate message should be displayed'''
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])
    
    def test_index_view_with_a_past_poll(self):
        '''Polls with a published date in the past should be displayed in the view'''
        create_poll(question="Hello", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello")
        self.assertQuerysetEqual(response.context['latest_poll_list'], ['<Poll: Hello>'])
        
    def test_index_view_with_a_future_poll(self):
        '''Polls with a published date in the past should not be displayed in the view'''
        create_poll(question="Hello", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])
    
    def test_index_view_with_a_past_and_a_future_poll(self):
        '''If Polls with a past and a future date exist, only the past date polls should be displayed'''
        create_poll(question="Past", days=-30)
        create_poll(question="Future", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Past")
        self.assertQuerysetEqual(response.context['latest_poll_list'], ['<Poll: Past>'])
    
    def test_index_view_with_two_polls(self):
        '''The poll page should display both poll data'''
        create_poll(question="Poll1", days=-30)
        create_poll(question="Poll2", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Poll1")
        self.assertContains(response, "Polls")
        self.assertQuerysetEqual(response.context['latest_poll_list'], ['<Poll: Poll1>', '<Poll: Poll2>'])

class PollIndexDetailTest(TestCase):
    def test_detail_view_with_a_future_poll(self):
        '''The detail view of a poll with a future pub_date should return a 404'''
        future_poll=create_poll(question="Future", days=30)
        response = self.client.get(reverse('polls:detail', args=(future_poll.id,)))
        self.assertEqual(response.status_code, 404)
    
    def test_detail_view_with_a_past_poll(self):
        '''The detail view of a poll with a past pub_date should display'''
        past_poll=create_poll(question="Past", days=-30)
        response = self.client.get(reverse('polls:detail', args=(past_poll.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Past")
        
        
        
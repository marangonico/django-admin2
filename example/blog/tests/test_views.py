from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from ..models import Post, Comment


class BaseIntegrationTest(TestCase):
    """
    Base TestCase for integration tests.
    """
    def setUp(self):
        self.client = Client()
        self.user = get_user_model()(username='user', is_staff=True,
                                     is_superuser=True)
        self.user.set_password("password")
        self.user.save()
        self.client.login(username='user', password='password')


class AdminIndexTest(BaseIntegrationTest):
    def test_view_ok(self):
        response = self.client.get(reverse("admin2:dashboard"))
        self.assertContains(response, reverse("admin2:blog_post_index"))


class PostListTest(BaseIntegrationTest):
    def test_view_ok(self):
        post = Post.objects.create(title="a_post_title", body="body")
        response = self.client.get(reverse("admin2:blog_post_index"))
        self.assertContains(response, post.title)


class PostDetailViewTest(BaseIntegrationTest):
    def test_view_ok(self):
        post = Post.objects.create(title="a_post_title", body="body")
        response = self.client.get(reverse("admin2:blog_post_detail",
                                           args=(post.pk, )))
        self.assertContains(response, post.title)


class PostCreateViewTest(BaseIntegrationTest):
    def test_view_ok(self):
        response = self.client.get(reverse("admin2:blog_post_create"))
        self.assertEqual(response.status_code, 200)

    def test_create_post(self):
        post_data = {
            "comment_set-TOTAL_FORMS": u'2',
            "comment_set-INITIAL_FORMS": u'0',
            "comment_set-MAX_NUM_FORMS": u'',
            "comment_set-0-body": u'Comment Body',
            "title": "a_post_title",
            "body": "a_post_body",
        }
 
        response = self.client.post(reverse("admin2:blog_post_create"),
                                    post_data,
                                    follow=True)
        self.assertTrue(Post.objects.filter(title="a_post_title").exists())
        post = Post.objects.get(title="a_post_title")
        comment = Comment.objects.get(body="Comment Body")
        self.assertRedirects(response, reverse("admin2:blog_post_index"))

    def test_save_and_add_another_redirects_to_create(self):
        """
        Tests that choosing 'Save and add another' from the model create 
        page redirects the user to the model create page.
        """
        post_data = {
            "comment_set-TOTAL_FORMS": u'2',
            "comment_set-INITIAL_FORMS": u'0',
            "comment_set-MAX_NUM_FORMS": u'',
            "title": "a_post_title",
            "body": "a_post_body",
            "_addanother": ""
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(reverse("admin2:blog_post_create"),
                                    post_data)
        post = Post.objects.get(title='a_post_title')
        self.assertRedirects(response, reverse("admin2:blog_post_create"))

    def test_save_and_continue_editing_redirects_to_update(self):
        """
        Tests that choosing "Save and continue editing" redirects 
        the user to the model update form.
        """
        post_data = {
            "comment_set-TOTAL_FORMS": u'2',
            "comment_set-INITIAL_FORMS": u'0',
            "comment_set-MAX_NUM_FORMS": u'',
            "title": "Unique",
            "body": "a_post_body",
            "_continue": ""
        }
        response = self.client.post(reverse("admin2:blog_post_create"),
                                    post_data)
        post = Post.objects.get(title="Unique")
        self.assertRedirects(response, reverse("admin2:blog_post_update",
                                               args=(post.pk, )))


class PostDeleteViewTest(BaseIntegrationTest):
    def test_view_ok(self):
        post = Post.objects.create(title="a_post_title", body="body")
        response = self.client.get(reverse("admin2:blog_post_delete",
                                           args=(post.pk, )))
        self.assertContains(response, post.title)

    def test_delete_post(self):
        post = Post.objects.create(title="a_post_title", body="body")
        response = self.client.post(reverse("admin2:blog_post_delete",
                                            args=(post.pk, )))
        self.assertRedirects(response, reverse("admin2:blog_post_index"))
        self.assertFalse(Post.objects.filter(pk=post.pk).exists())

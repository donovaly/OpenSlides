from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.forms.models import modelform_factory

class PollFormView(TemplateView):
    template_name = 'poll/poll.html'
    poll_argument = 'poll_id'

    def set_poll(self, poll_id):
        poll_id = poll_id
        self.poll = self.poll_class.objects.get(pk=poll_id)

    def get_context_data(self, **kwargs):
        context = super(PollFormView, self).get_context_data(**kwargs)
        self.set_poll(self.kwargs['poll_id'])
        context['poll'] = self.poll
        if 'forms' in kwargs:
            context['forms'] = kwargs['forms']
            context['pollform'] = kwargs['pollform']
        else:
            context['forms'] = self.poll.get_vote_forms()
            FormClass = self.get_modelform_class()
            context['pollform'] = FormClass(instance=self.poll, prefix='pollform')
        return context

    def get_success_url(self):
        return self.success_url

    def get_modelform_class(self):
        fields = []
        self.poll.append_pollform_fields(fields)
        return modelform_factory(self.poll.__class__, fields=fields)

    def post(self, request, *args, **kwargs):
        self.set_poll(self.kwargs['poll_id'])
        forms = self.poll.get_vote_forms(data=self.request.POST)

        FormClass = self.get_modelform_class()
        pollform = FormClass(data=self.request.POST, instance=self.poll, prefix='pollform')

        error = False
        for form in forms:
            if not form.is_valid():
                error = True

        if not pollform.is_valid():
            error = True

        if error:
            return self.render_to_response(self.get_context_data(
                forms=forms,
                pollform=pollform,
            ))

        for form in forms:
            data = {}
            for value in self.poll.vote_values:
                data[value] = form.cleaned_data[value]
            self.poll.set_form_values(form.option, data)

        pollform.save()
        return HttpResponseRedirect(self.get_success_url())
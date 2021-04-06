from django.shortcuts import render, redirect
from .models import UsageType, Usage
from carbon_usage.permissions import IsOwner
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from .serializers import UsageSerializer, UsageTypeSerializer, UserSerializer
from rest_framework import generics
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_exempt
from rest_framework import filters


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UsageViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = UsageSerializer
    ordering_fields = ['usage_at', 'usage_type']
    filter_backends = [filters.OrderingFilter]

    def get_queryset(self):
        # Filter by user
        user = self.request.user
        queryset = Usage.objects.filter(user=user)

        # If timerange_start query param, filter
        # out usage's before given datetime
        timerange_start = self.request.query_params.get('timerange_start')
        if timerange_start is not None:
            print("Timerange start: %s " % timerange_start)
            queryset = queryset.filter(usage_at__gte=timerange_start)

        # If timerange_end query param, filter out usage's after given datetime
        timerange_end = self.request.query_params.get('timerange_end')
        if timerange_end is not None:
            print(timerange_end)
            queryset = queryset.filter(usage_at__lte=timerange_end)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UsageTypeViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated]
    ordering_fields = ['unit', 'name']
    filter_backends = [filters.OrderingFilter]
    queryset = UsageType.objects.all().order_by('id')
    serializer_class = UsageTypeSerializer


# Breaking from viewsets for user signup routine, to use
# django built in tooling, using their user model instead of
# rolling my own

# Using this decorate to allow creating a user
# via my testing script. Not to be used in production
@csrf_exempt
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/carbon_usage')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

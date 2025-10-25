import decimal
from decimal import Decimal
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q, Exists, OuterRef, Max
from django.utils import timezone
from django.urls import reverse_lazy

from rides.models import Ride, RideEvent
from accounts.models import CustomUser
from .forms import StaffCreateUserForm, AddBalanceForm


# ----------------------------
# Mixins
# ----------------------------
class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


# ----------------------------
# Dashboard Home / Staff Dashboard
# ----------------------------
class StaffDashboardView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
    template_name = 'dashboard/staff_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Users
        riders = CustomUser.objects.filter(user_role='RIDER')
        customers = CustomUser.objects.filter(user_role='CUSTOMER')
        context['total_users'] = riders.count() + customers.count()
        context['total_riders'] = riders.count()
        context['total_customers'] = customers.count()

        # Ride statistics
        today = timezone.now().date()
        context['active_rides'] = Ride.objects.filter(status__in=['ACCEPTED', 'ONGOING']).count()
        context['today_rides'] = Ride.objects.filter(created_at__date=today).count()
        context['completed_rides'] = Ride.objects.filter(status='COMPLETED').count()
        context['total_earnings'] = Ride.objects.filter(status='COMPLETED').aggregate(total=Sum('price'))['total'] or 0

        # System balance
        context['total_system_balance'] = CustomUser.objects.aggregate(total=Sum('balance'))['total'] or 0

        # Riders stats
        riders_data = riders.annotate(
            completed_rides_count=Count('rides_as_rider', filter=Q(rides_as_rider__status='COMPLETED')),
            total_earnings=Sum('rides_as_rider__price', filter=Q(rides_as_rider__status='COMPLETED')),
            has_active_ride=Exists(Ride.objects.filter(rider=OuterRef('pk'), status__in=['ACCEPTED', 'ONGOING']))
        )
        context['riders'] = riders_data

        # Customers stats
        customers_data = customers.annotate(
            total_rides_count=Count('rides_as_customer'),
            total_spent=Sum('rides_as_customer__price', filter=Q(rides_as_customer__status='COMPLETED')),
            last_activity=Max('rides_as_customer__created_at')
        )
        context['customers'] = customers_data

        # Recent events
        context['recent_events'] = RideEvent.objects.select_related('ride').order_by('-created_at')[:20]

        return context


# ----------------------------
# Ride Views
# ----------------------------
class StaffRideListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Ride
    template_name = 'dashboard/ride_list.html'
    context_object_name = 'rides'
    paginate_by = 20

    def get_queryset(self):
        queryset = Ride.objects.all()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filters'] = Ride.STATUS_CHOICES
        return context


class StaffRideDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    model = Ride
    template_name = 'dashboard/ride_detail.html'
    context_object_name = 'ride'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = self.object.events.all().order_by('-created_at')
        context['can_edit'] = True
        return context


# ----------------------------
# Ride Event List
# ----------------------------
class StaffEventListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = RideEvent
    template_name = 'dashboard/event_list.html'
    context_object_name = 'events'
    paginate_by = 50

    def get_queryset(self):
        return RideEvent.objects.all().select_related('ride').order_by('-created_at')


# ----------------------------
# User Views
# ----------------------------
class StaffUserListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = CustomUser
    template_name = 'dashboard/user_list.html'
    context_object_name = 'users'
    paginate_by = 50

    def get_queryset(self):
        queryset = CustomUser.objects.all()
        role = self.request.GET.get('role')
        if role:
            queryset = queryset.filter(user_role=role)
        return queryset.order_by('-date_joined')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role_filters'] = CustomUser.ROLE_CHOICES
        return context


class StaffCreateUserView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = CustomUser
    form_class = StaffCreateUserForm
    template_name = 'dashboard/create_user.html'
    success_url = reverse_lazy('staff-users')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'User {self.object.username} created successfully with role {self.object.get_user_role_display()}!'
        )
        return response


# ----------------------------
# Add Balance
# ----------------------------
@login_required
@user_passes_test(lambda u: u.is_staff)
def add_balance(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        form = AddBalanceForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            note = form.cleaned_data['note']
            user.balance += Decimal(amount)
            user.save()
            messages.success(
                request,
                f'Successfully added {amount} to {user.get_full_name()}\'s balance. New balance: {user.balance}'
            )
            return redirect('staff-user-detail', pk=user_id)
    else:
        form = AddBalanceForm()

    return render(request, 'dashboard/add_balance.html', {'form': form, 'user': user})


@login_required
@user_passes_test(lambda u: u.is_staff)
def add_staff_balance(request):
    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', '0'))
            if amount <= 0:
                messages.error(request, 'Please enter a positive amount.')
                return redirect('staff-dashboard')

            request.user.balance += amount
            request.user.save()

            messages.success(
                request,
                f'Successfully added ₱{amount:.2f} to your balance. New balance: ₱{request.user.balance:.2f}'
            )
        except (ValueError, decimal.InvalidOperation):
            messages.error(request, 'Invalid amount entered.')

    return redirect('staff-dashboard')


# ----------------------------
# Customer Dashboard
# ----------------------------
@login_required
def customer_dashboard(request):
    return render(request, 'customer.html')

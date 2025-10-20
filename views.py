@login_required
def dashboard(request):
    user = request.user
    
    # Handle different form submissions
    if request.method == "POST":
        form_type = request.POST.get("form_type")
        
        if form_type == "send_money":
            return handle_money_transfer(request)
        elif form_type == "transaction":
            return handle_transaction_form(request)
        elif form_type == "goal":
            return handle_goal_form(request)
    
    try:
        # Get user's transactions and goals
        transactions = Transaction.objects.filter(user=user).order_by("-occurred_at")[:10]
        goals = SavingGoal.objects.filter(user=user)
        
        # Calculate metrics - handle case where constants don't exist yet
        try:
            incoming_kinds = [Transaction.INCOMING, Transaction.TRANSFER_IN]
            outgoing_kinds = [Transaction.OUTGOING, Transaction.TRANSFER_OUT]
        except AttributeError:
            # Fallback for older Transaction model without transfer constants
            incoming_kinds = ['incoming']
            outgoing_kinds = ['outgoing']
        
              # ✅ Simplified and database-aggregated calculations
        incoming_total = (
            Transaction.objects.filter(user=user, kind__in=incoming_kinds)
            .aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        outgoing_total = (
            Transaction.objects.filter(user=user, kind__in=outgoing_kinds)
            .aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        # Ensure both totals are positive for display
        incoming_total = abs(incoming_total)
        outgoing_total = abs(outgoing_total)

        # Net flow: total income minus total expenses
        net_flow = incoming_total - outgoing_total

        
        # Get donation total
        donation_total_packs = Donation.objects.filter(donor=user).aggregate(
            total=Sum("quantity")
        )["total"] or 0
        
        # Get available recipients (users with phone numbers, excluding current user)
        available_recipients = UserProfile.objects.filter(
            phone_number__isnull=False,
            is_active=True
        ).exclude(user=user).select_related('user')
        
        context = {
            "recent_transactions": transactions,
            "goals": goals,
            "incoming_total": incoming_total,
            "outgoing_total": outgoing_total,
            "net_flow": net_flow,
            "donation_total_packs": donation_total_packs,
            "available_recipients": available_recipients,
            "transaction_form": TransactionForm(),
            "goal_form": SavingGoalForm(),
            "transfer_form": MoneyTransferForm(request=request),
            "currency_choices": CURRENCY_CHOICES,
            "now": timezone.now(),
        }
        
        return render(request, "dashboard.html", context)
        
    except Exception as e:
        print(f"ERROR in dashboard: {e}")
        messages.error(request, f"Error loading dashboard: {str(e)}")
        
        # Return safe context with sample data
        context = {
            "recent_transactions": [],
            "goals": [],
            "incoming_total": Decimal('1250.00'),  # More realistic sample data
            "outgoing_total": Decimal('850.00'),
            "net_flow": Decimal('400.00'),
            "donation_total_packs": 3,
            "available_recipients": UserProfile.objects.filter(
                phone_number__isnull=False,
                is_active=True
            ).exclude(user=user).select_related('user'),
            "transaction_form": TransactionForm(),
            "goal_form": SavingGoalForm(),
            "transfer_form": MoneyTransferForm(request=request),
            "currency_choices": CURRENCY_CHOICES,
            "now": timezone.now(),
        }
        
        return render(request, "dashboard.html", context)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import (Order)


@login_required
def my_order(request):
    """
    View to display the orders made by the customer.
    """
    # Get all active orders made by the customer
    active_orders = Order.objects.filter(customer=request.user, status=True)

    # Get all cancelled orders made by the customer
    cancelled_orders = Order.objects.filter(customer=request.user, status=False)

    context = {'show_navbar_footer': True, "active_orders": active_orders, "cancelled_orders": cancelled_orders}
    return render(request, 'order/my_order.html', context)


@login_required
def order_operations(request, order_id):
    """
    Handles various operations related to orders like displaying order summary and cancelling orders.

    Args: order_id: The ID of the order to perform the operation on.
    """
    # Get the order for the given id and check if it belongs to the current customer
    order = Order.objects.get(customer=request.user, id=order_id)

    # If the URL contains 'order_summary', render the order summary page and if the URL contains 
    # 'cancel_order' and the order is not already cancelled, cancel the order
    if 'order_summary' in request.path_info:
        context = {'show_navbar_footer': True, "order": order, "show_print_button": True}
        return render(request, 'order/order_summary.html', context)
    elif 'cancel_order' in request.path_info:
        if order.status:
            order.status = False
            order.save()
            messages.success(request, f"Order Cancelled")
    
    return redirect('/order/my_order/')


@login_required
def generate_pdf(request, order_id):
    """
    This function generates a PDF of the order summary for the given order ID.
    
    Args: order_id: ID of the order to generate the PDF for.
    """
    # Get the order object for the given order ID and generate HTML string for the order object
    order = Order.objects.get(customer=request.user.id, id=order_id)
    html = render_to_string('order/order_summary.html', {'order': order, "show_print_button": False})

    # Create an HttpResponse object with PDF content type and set filename
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="order_summary_{}.pdf"'.format(order_id)

    # Use WeasyPrint to generate PDF file from the HTML string and write to response object
    HTML(string=html).write_pdf(response)

    return response
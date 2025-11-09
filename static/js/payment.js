// Razorpay Payment Integration
// Handles payment processing for crop purchases

let razorpayKey = null;

// Initialize Razorpay
async function initRazorpay() {
    try {
        const response = await fetch('/api/payment/get-key');
        const data = await response.json();
        
        if (data.success) {
            razorpayKey = data.key;
            console.log('Razorpay initialized with key:', razorpayKey);
        } else {
            console.error('Failed to get Razorpay key:', data.error);
        }
    } catch (error) {
        console.error('Error initializing Razorpay:', error);
    }
}

// Create payment order and open Razorpay checkout
async function initiatePayment(amount, description = 'Crop Purchase', orderData = {}) {
    try {
        // Ensure Razorpay script is loaded
        await loadRazorpayScript();
        
        if (!razorpayKey) {
            await initRazorpay();
        }
        
        if (!razorpayKey) {
            alert('Payment gateway is not available. Please try again later.');
            return;
        }
        
        if (typeof Razorpay === 'undefined') {
            alert('Payment gateway is loading. Please wait a moment and try again.');
            return;
        }
        
        // Create order on server
        const orderResponse = await fetch('/api/payment/create-order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                amount: amount,
                currency: 'INR',
                order_type: 'crop_purchase',
                ...orderData
            })
        });
        
        const orderData_response = await orderResponse.json();
        
        if (!orderData_response.success) {
            alert('Failed to create payment order: ' + orderData_response.error);
            return;
        }
        
        const order = orderData_response.order;
        
        // Store order data for later use
        window.currentOrderData = orderData;
        
        // Razorpay checkout options
        const options = {
            key: razorpayKey,
            amount: order.amount,
            currency: order.currency,
            name: 'Farming App',
            description: description,
            order_id: order.id,
            handler: async function(response) {
                // Payment successful, verify on server
                // Pass original amount in rupees, not order.amount (which is in paise)
                await verifyPayment(response, amount, orderData);
            },
            prefill: {
                name: sessionStorage.getItem('userName') || '',
                email: sessionStorage.getItem('userEmail') || '',
                contact: sessionStorage.getItem('userPhone') || ''
            },
            theme: {
                color: '#28a745'
            },
            modal: {
                ondismiss: function() {
                    console.log('Payment cancelled by user');
                    window.currentOrderData = null;
                }
            }
        };
        
        // Open Razorpay checkout
        const razorpay = new Razorpay(options);
        razorpay.open();
        
    } catch (error) {
        console.error('Error initiating payment:', error);
        alert('An error occurred while processing payment. Please try again.');
    }
}

// Verify payment on server
async function verifyPayment(paymentResponse, amount, orderData = {}) {
    try {
        const verifyResponse = await fetch('/api/payment/verify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                razorpay_order_id: paymentResponse.razorpay_order_id,
                razorpay_payment_id: paymentResponse.razorpay_payment_id,
                razorpay_signature: paymentResponse.razorpay_signature,
                amount: amount,
                ...orderData
            })
        });
        
        const verifyData = await verifyResponse.json();
        
        if (verifyData.success) {
            // Payment verified successfully
            showPaymentSuccess(verifyData.payment_id, verifyData.crop_sold_out);
            
            // Clear stored order data
            window.currentOrderData = null;
            
            // Trigger custom event for payment success
            window.dispatchEvent(new CustomEvent('paymentSuccess', {
                detail: {
                    payment_id: verifyData.payment_id,
                    order_id: paymentResponse.razorpay_order_id,
                    crop_sold_out: verifyData.crop_sold_out,
                    ...orderData
                }
            }));
            
            // Reload page after 2 seconds to show updated stock
            setTimeout(() => {
                location.reload();
            }, 2000);
        } else {
            showPaymentError(verifyData.error || 'Payment verification failed');
        }
    } catch (error) {
        console.error('Error verifying payment:', error);
        showPaymentError('An error occurred while verifying payment.');
    }
}

// Show payment success message
function showPaymentSuccess(paymentId, cropSoldOut = false) {
    // Create success modal or alert
    const soldOutMessage = cropSoldOut ? '<p style="color: #dc3545; font-weight: 600; margin-top: 10px;">⚠️ This item is now sold out!</p>' : '';
    const successHtml = `
        <div class="payment-success-modal" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        ">
            <div style="
                background: white;
                padding: 30px;
                border-radius: 10px;
                text-align: center;
                max-width: 400px;
            ">
                <div style="font-size: 60px; margin-bottom: 20px;">✅</div>
                <h2 style="color: #28a745; margin-bottom: 10px;">Payment Successful!</h2>
                <p style="color: #666; margin-bottom: 20px;">Your payment has been processed successfully.</p>
                ${soldOutMessage}
                <p style="font-size: 12px; color: #999; margin-top: 15px;">Payment ID: ${paymentId}</p>
                <p style="font-size: 11px; color: #999; margin-top: 5px;">Page will refresh automatically...</p>
                <button onclick="this.closest('.payment-success-modal').remove(); location.reload();" style="
                    background: #28a745;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    margin-top: 20px;
                ">Close & Refresh</button>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', successHtml);
}

// Show payment error message
function showPaymentError(errorMessage) {
    alert('Payment Error: ' + errorMessage);
}

// Load Razorpay script
function loadRazorpayScript() {
    return new Promise((resolve, reject) => {
        if (typeof Razorpay !== 'undefined') {
            resolve();
            return;
        }
        
        const script = document.createElement('script');
        script.src = 'https://checkout.razorpay.com/v1/checkout.js';
        script.onload = function() {
            console.log('Razorpay checkout script loaded');
            resolve();
        };
        script.onerror = function() {
            console.error('Failed to load Razorpay script');
            reject(new Error('Failed to load Razorpay script'));
        };
        document.head.appendChild(script);
    });
}

// Initialize Razorpay when page loads
document.addEventListener('DOMContentLoaded', function() {
    initRazorpay();
    loadRazorpayScript().catch(err => console.error('Razorpay script loading error:', err));
});

// Make functions globally accessible
window.initiatePayment = initiatePayment;
window.initRazorpay = initRazorpay;
window.loadRazorpayScript = loadRazorpayScript;


from email import send_email
from order import create_order
from payment import process_payment

def main():
    print("Starting order process...")

    order = create_order("상품 A", 2)
    print(f"Order created: {order}")

    payment_result = process_payment(order, "신용카드")
    print(f"Payment result: {payment_result}")

    send_email("customer@example.com", "주문이 완료되었습니다.")
    print("Confirmation email sent.")

if __name__ == "__main__":
    main()


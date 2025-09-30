import streamlit as st

def calculator():
    st.title("🧮 Interactive Calculator")
    st.markdown("Perform basic arithmetic operations with error handling.")

    # Inputs
    col1, col2 = st.columns(2)
    with col1:
        a = st.text_input("Enter first number:")
    with col2:
        b = st.text_input("Enter second number:")

    operation = st.radio("Choose operation", ["Add", "Subtract", "Multiply", "Divide"])

    if st.button("Calculate"):
        try:
            a = float(a)
            b = float(b)
            if operation == "Add":
                result = a + b
            elif operation == "Subtract":
                result = a - b
            elif operation == "Multiply":
                result = a * b
            elif operation == "Divide":
                if b == 0:
                    st.error("❌ Error: Division by zero is not allowed.")
                    return
                result = a / b
            st.success(f"✅ Result: {result}")
        except ValueError:
            st.error("❌ Please enter valid numeric values.")

if __name__ == "__main__":
    calculator()

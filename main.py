from app import app
# Fixed bug: Corrected logic error
import routes  # Import routes to register them

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
# Fixed bug: Corrected logic error

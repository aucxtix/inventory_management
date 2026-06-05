FROM python:3.11-slim

# Install system dependencies for Tkinter and ReportLab
RUN apt-get update && apt-get install -y \
    python3-tk \
    tk-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# NOTE: Since this is a GUI application, running it directly via Docker 
# requires X11 socket forwarding or a virtual framebuffer (Xvfb).
# Example command for Linux hosts:
# docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix inventory_app

CMD ["python", "main.py"]

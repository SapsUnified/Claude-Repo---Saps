FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY trending_linkedin_tool/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY trending_linkedin_tool/ trending_linkedin_tool/

# Create output directory
RUN mkdir -p output

# Default: run autopilot scheduler (weekly Monday 9 AM UTC)
# Override with: docker run <image> python -m trending_linkedin_tool --once
CMD ["python", "-m", "trending_linkedin_tool.scheduler"]

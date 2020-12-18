FROM python:3.8.6-slim-buster

# Add crontab file in the cron directory
ADD crontab /etc/cron.d/hello-cron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/hello-cron

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Install Cron & Editor
RUN apt-get update
RUN apt-get -y install vim cron

WORKDIR /home/app

#COPY stocksymbols ./stocksymbols
#COPY cron.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

# Run the command on container startup
CMD cron && tail -f /var/log/cron.log
# CMD ["cron", "-f"]

#Quick note about a gotcha:
#If you're adding a script file and telling cron to run it, remember to
#RUN chmod 0744 /the_script
#Cron fails silently if you forget.
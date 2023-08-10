FROM cern/cc7-base:latest

RUN curl -sL https://rpm.nodesource.com/setup_10.x | bash -
RUN yum -y update && yum clean all && yum -y install git python-pip python-virtualenv nodejs gcc-c++ make && yum clean all 
VOLUME /data /xsdbdir /venv
WORKDIR /xsdbdir/xsecdb
COPY ./ /xsdbdir/xsecdb
RUN cd client && npm install && npm install --save history && npm run compile && cd ..
RUN  pip install -r requirements.txt
CMD exec python main.py  
# FROM ubuntu:16.04
FROM coinstac/coinstac-base-python-stream
ENV MCRROOT=/usr/local/MATLAB/MATLAB_Runtime/v91
ENV MCR_CACHE_ROOT=/tmp
RUN printf "deb http://archive.debian.org/debian/ jessie main\ndeb-src http://archive.debian.org/debian/ jessie main\ndeb http://security.debian.org jessie/updates main\ndeb-src http://security.debian.org jessie/updates main" > /etc/apt/sources.list

RUN apt-get update

#Update this section on 10/17/2020
RUN apt-get install -y --force-yes  python3-gi python3-dbus python3-software-properties
RUN apt-get install -y --force-yes  software-properties-common
RUN apt-get install -y --force-yes zip \
    unzip

#Update this section on 10/17/2020
RUN apt-get install -y --force-yes 		libjasper-runtime
RUN apt-get install -y --force-yes      libx11-dev 
RUN apt-get install -y --force-yes      libxcomposite-dev 
RUN apt-get install -y --force-yes    	libxcursor-dev 
RUN apt-get install -y --force-yes      libxdamage-dev 
RUN apt-get install -y --force-yes      libxext-dev 
RUN apt-get install -y --force-yes    	libxfixes-dev 
RUN apt-get install -y --force-yes      libxft-dev 
RUN apt-get install -y --force-yes      libxi-dev 
RUN apt-get install -y --force-yes    	libxrandr-dev 
RUN apt-get install -y --force-yes      libxt-dev 
RUN apt-get install -y --force-yes      libxtst-dev 
RUN apt-get install -y --force-yes    	libxxf86vm-dev 
RUN apt-get install -y --force-yes      libasound2-dev 
RUN apt-get install -y --force-yes      libatk1.0-dev 
RUN apt-get install -y --force-yes    	libcairo2-dev 
RUN apt-get install -y --force-yes      gconf2 
RUN apt-get install -y --force-yes    	libsndfile1-dev 
RUN apt-get install -y --force-yes      libxcb1-dev 
RUN apt-get install -y --force-yes      libxslt-dev 
RUN apt-get install -y --force-yes    	curl 
RUN apt-get install -y --force-yes    	libgtk-3-dev

RUN mkdir /tmp/mcr_installer && \
    cd /tmp/mcr_installer && \
    wget http://ssd.mathworks.com/supportfiles/downloads/R2016b/deployment_files/R2016b/installers/glnxa64/MCR_R2016b_glnxa64_installer.zip && \
    unzip MCR_R2016b_glnxa64_installer.zip && \
    ./install -mode silent -agreeToLicense yes && \
    rm -Rf /tmp/mcr_installer

# Copy the current directory contents into the container
WORKDIR /computation
COPY requirements.txt /computation

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

COPY . /computation

COPY ./coinstac_spatially_constrained_ica/nipype-0.10.0/nipype/interfaces/gift /usr/local/lib/python3.6/site-packages/nipype/interfaces/gift

RUN mkdir /output

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone

from proxmoxer import ProxmoxAPI
from django.shortcuts import render

from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required

from subprocess import call, Popen

import time
import os
import stat

from .models import Connection, UserConnection, NodePassword

import logging


logger = logging.getLogger(__name__)
proxmox = None
proxmox_connection_id = None


def toggle_virt(virt_id, node_name, cls): #toggle start/stop of a container or virtual machine
    logger.warning("toggle")
    logger.warning(virt_id)
    logger.warning(node_name)
    logger.warning(cls)
    cls_system = "lxc" if cls == "ct" else "qemu"
    
    global proxmox
    for node in proxmox.nodes.get(): #fornow, for cycle is just to get status 
    	if node['node'] != node_name:
    		continue
    	if cls_system == "lxc":
    		for vm in proxmox.nodes(node['node']).lxc.get():
    			if int(vm['vmid']) == int(virt_id):
    				toggled_status = "start" if vm['status'] == "stopped" else "stop"
    				post_string = f"nodes/{node['node']}/{cls_system}/{virt_id}/status/{toggled_status}"
    				proxmox.post(post_string)
    	else:		
    		for vm in proxmox.nodes(node['node']).qemu.get():
    			if int(vm['vmid']) == int(virt_id):
    				toggled_status = "start" if vm['status'] == "stopped" else "stop"
    				post_string = f"nodes/{node['node']}/{cls_system}/{virt_id}/status/{toggled_status}"
    				proxmox.post(post_string)
	
def delete_virt(virt_id, node_name, cls): #delete a container or virtual machine
    logger.warning("delete")
    logger.warning(virt_id)
    logger.warning(node_name)
    cls_system = "lxc" if cls == "ct" else "qemu"
    
    global proxmox
    proxmox.delete(f"nodes/{node_name}/{cls_system}/{virt_id}")
        		
def create_container(request, connection_id):
    node_name = request.POST['nodename']
    
    vmid = request.POST['vmid']
    ostemplate = request.POST['ostemplate']
    hostname = request.POST['hostname']
    storage = request.POST['storage']    
    cores = request.POST['cores']
    memory = request.POST['memory']
    swap = request.POST['swap']
    net0 = request.POST['net0']
    password = request.POST['password']
    
    for node in proxmox.nodes.get():
        if node['node'] == node_name:
            proxmox.nodes(node['node']).lxc.create(
                vmid=vmid,
                ostemplate=ostemplate,
                hostname=hostname,
                storage=storage,
                cores=cores,
                memory=memory,
                swap=swap,
                net0=net0,
                password=password)

def create_vm(request, connection_id):
    node_name = request.POST['nodename']
    vmid = request.POST['vmid']
    proxmox.nodes(node_name).qemu.create(vmid=vmid)

def download_template(request, connection_id):
	node_name = request.POST['nodename']
	storage = request.POST['storage']
	download_url = request.POST['template_url']
	
	post_string = f"nodes/{node_name}/storage/{storage}/{download_url}"
	
	proxmox.post(post_string)
	
def parse_id_node(post_key, letter):
	print("PARSE_ID")
	print(post_key)
	str_id = post_key[: post_key.find(letter)]
	str_node = post_key[post_key.find(letter) + 1:][:-2]
	str_class = post_key[-2] + post_key[-1]
	return str_id, str_node, str_class


def getIpsDict(nodename, password, connection_id):
	host = Connection.objects.get(pk=connection_id).host

	unix_script = f"sshpass -p {password} ssh -o StrictHostKeyChecking=no root@{host} 'lxc-ls -f' >ips.txt"
	print(unix_script)
	temp_file = open("temp_file.sh", "w")
	temp_file.write(unix_script)
	temp_file.close()
	
	st = os.stat('temp_file.sh')
	os.chmod('temp_file.sh', st.st_mode | stat.S_IEXEC)
	
	rc = Popen("./temp_file.sh", shell = True)
	
	print(host)
	print(password)
	
	# wait ips to write down
	time.sleep(1)
	rc2 = call("pwd")
	ips_file = open("ips.txt", 'r')
	lines = ips_file.readlines()
	print(lines)
	return_dict = {}
	for line in lines[1:]:
		nl = line.split()
		print(nl[0], nl[4], nl[5])
		return_dict[nl[0]] = nl[4] if nl[4] != "-" else nl[5]
		logger.warning("container checked")

	logger.warning(str(return_dict))
	return return_dict

@login_required
def results(request, username, connection_id):    	   	     
    logger.warning("results")
    if request.method == "POST":
    	logger.warning("POST")
    	logger.warning(str(request.POST.keys()))
	
    	if "Refresh" in request.POST.keys():
   	   return HttpResponseRedirect(reverse('connection:results', args=(username, connection_id)))
    	if "Create ct" in request.POST.keys():
    	   create_container(request, connection_id)
    	   return HttpResponseRedirect(reverse('connection:results', args=(username, connection_id)))
    	if "Create vm" in request.POST.keys():
    	   create_vm(request, connection_id)
    	   return HttpResponseRedirect(reverse('connection:results', args=(username, connection_id)))
    	if "template_url" in request.POST.keys():
    	   logger.warning("template_url")
    	   download_template(request, connection_id)
    	   
    	   return HttpResponseRedirect(reverse('connection:results', args=(username, connection_id)))
    	virt_id = None
    	for k in request.POST.keys():
    		if (k[0] == 's'):
    			virt_id, node_name, cls = parse_id_node(k[1:], 's')
    			if virt_id is not None:
    				toggle_virt(virt_id, node_name, cls)
    			break
    		elif (k[0] == 'd'):
    			virt_id, node_name, cls = parse_id_node(k[1:], 'd')
    			if virt_id is not None:
    				delete_virt(virt_id, node_name, cls)
    			break
    	return HttpResponseRedirect(reverse('connection:results', args=(username, connection_id)))
    
    global proxmox
    res = "Connection id:"
    global proxmox_connection_id
    res += str(proxmox_connection_id)
    virts = []
    for node in proxmox.nodes.get():
    	nodename = node['node']
    	password = NodePassword.objects.filter(nodename=nodename, connection=connection_id).values('password').first().get('password')
     	
    	ips_dict = getIpsDict(nodename, password, connection_id)

    	for vm in proxmox.nodes(node['node']).lxc.get():
        	virts.append((vm['vmid'], vm['name'], node['node'], vm['status'], ips_dict.get(str(vm['vmid'])), 'ct'))
        	
    	for vm in proxmox.nodes(node['node']).qemu.get():
        	virts.append((str(vm['vmid']), vm['name'], node['node'], vm['status'], ips_dict.get(str(vm['vmid'])), 'vm')) #str(vm['vmid']) vms go with int fsr 

    virts = list(sorted(virts))
   
    return render(request, 'connection/results.html', {'res': res, 'virts' : virts})

def connect(request, connection_id):
    global proxmox_connection_id
    proxmox_connection_id = connection_id
    
    current_connection = Connection.objects.get(pk=connection_id)
   
    host = current_connection.host
    backend = current_connection.backend
    service = current_connection.service
    user = current_connection.user
    password = current_connection.password
    verify_ssl = current_connection.verify_ssl
    port = current_connection.port
	
    global proxmox
    proxmox = ProxmoxAPI(
    host=host, backend=backend, service=service, user=user, password=password,
    verify_ssl=verify_ssl, port=port)

def create_connection(request): #unused
    host = request.POST['host']
    backend = request.POST['backend']
    service = request.POST['service']
    user = request.POST['user']
    password = request.POST['password']
    verify_ssl = "True" if request.POST['verify_ssl'] == "True" else "False"
    port = int(request.POST['port'])
    cur_date = timezone.now()
    
    new_connection = Connection(host=host,
    				 backend=backend,
    				 service=service, 
    				 user=user, 
    				 password=password,
    				 verify_ssl=verify_ssl,
    				 port=port, 
    				 date=cur_date)
    new_connection.save()

def auth(request):
    if request.method != "POST":
    	logger.warning("NOT POST")
    	return render(request, 'connection/auth.html')

    username = request.POST['login']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse('connection:user', args=(username,)))
    return render(request, 'connefction/auth.html')

@login_required
def user(request, username): 
    if request.method == "POST":
    	logger.warning("POST")
    	logout(request)
    	return HttpResponseRedirect(reverse('connection:auth', args=()))
    	
    users_connection = UserConnection.objects.filter(username=username).values('connection')
    context = {'connections' :Connection.objects.filter(pk__in=users_connection).all(), 'username' : username}
    
    return render(request, 'connection/user.html', context) 

@login_required    
def detail(request, username, connection_id):
    if request.method == "POST":
    	connect(request, connection_id)
    	return HttpResponseRedirect(reverse('connection:results', args=(username,connection_id)))
    connection = get_object_or_404(Connection, pk=connection_id)
    return render(request, 'connection/detail.html', {'connection': connection})
    

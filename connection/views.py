from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone

from proxmoxer import ProxmoxAPI
from django.shortcuts import render

from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required



from .models import Connection
from .models import UserConnection

import logging


logger = logging.getLogger(__name__)
proxmox = None
proxmox_connection_id = None


def toggle_virt(virt_id, node_name): #toggle start/stop of a container or virtual machine
    logger.warning("toggle")
    logger.warning(virt_id)
    logger.warning(node_name)
    global proxmox
    for node in proxmox.nodes.get():
    	if node['node'] != node_name:
    		continue
    	
    	for vm in proxmox.nodes(node['node']).lxc.get():
        	if int(vm['vmid']) == int(virt_id):
        		logger.warning(vm['status'])
        		logger.warning(vm)
        		
        		toggled_status = "start" if vm['status'] == "stopped" else "stop"
        		post_string = f"nodes/{node['node']}/lxc/{virt_id}/status/{toggled_status}"
        		print(post_string)
        		proxmox.post(post_string)
        		#proxmox.nodes(node['node']).lxc.post("nodes/{l}/lxc/102/status/stop")
        		break

def create_container(request, connection_id):
    node_name = request.POST['nodename']
    
    vmid = request.POST['vmid']
    ostemplate = request.POST['ostemplate']
    hostname = request.POST['hostname']
    storage= request.POST['storage']    
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

def download_template(request, connection_id):
	node_name = request.POST['nodename']
	storage = request.POST['storage']
	download_url = request.POST['template_url']
	
	post_string = f"nodes/{node_name}/storage/{storage}/{download_url}"
	
	proxmox.post(post_string)
	
def parse_id_node(post_key):
	str_id = post_key[: post_key.find('s')]
	str_node = post_key[post_key.find('s') + 1:]
	return str_id, str_node

@login_required
def results(request, username, connection_id):    	   	
    connect(request, connection_id)
     
    logger.warning("results")
    if request.method == "POST":
    	logger.warning("POST")
    	logger.warning(str(request.POST.keys()))
	
    	if "Refresh" in request.POST.keys():
   	   return HttpResponseRedirect(reverse('connection:results', args=(username, connection_id)))
    	
    	if "ostemplate" in request.POST.keys():
    	   create_container(request, connection_id)
    	   return HttpResponseRedirect(reverse('connection:results', args=(username, connection_id)))
    	if "template_url" in request.POST.keys():
    	   logger.warning("template_url")
    	   download_template(request, connection_id)
    	   
    	   return HttpResponseRedirect(reverse('connection:results', args=(username, connection_id)))
    	virt_id = None
    	for k in request.POST.keys():
    		if (k[0] == 's'):
    			virt_id, node_name = parse_id_node(k[1:])
    			break
    	if virt_id is not None:
    		toggle_virt(virt_id, node_name)
    	return HttpResponseRedirect(reverse('connection:results', args=(username, connection_id)))
 
    global proxmox
    res = "Connection id:"
    global proxmox_connection_id
    res += str(proxmox_connection_id)
    virts = []
    for node in proxmox.nodes.get():
    	for vm in proxmox.nodes(node['node']).lxc.get():
        	get_string = f"nodes/{node['node']}/lxc/{vm['vmid']}/config"
        	c = proxmox.get(get_string)
        	logger.warning(str(c))

        	virts.append((vm['vmid'], vm['name'], node['node'], vm['status']))
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
    return render(request, 'connection/auth.html')

@login_required
def user(request, username): #ну не в один запрос пока что
    users_connection = UserConnection.objects.filter(username=username).values('connection')
    context = {'connections' :Connection.objects.filter(pk__in=users_connection).all(), 'username' : username}
    
    if not request.user.is_authenticated:
        print("HELL NO")
    else:
    	print("K")
    return render(request, 'connection/user.html', context) 

@login_required    
def detail(request, username, connection_id):
    if request.method == "POST":
    	logger.warning("NOT POST")
    	return HttpResponseRedirect(reverse('connection:results', args=(username,connection_id)))
    connection = get_object_or_404(Connection, pk=connection_id)
    return render(request, 'connection/detail.html', {'connection': connection})
    

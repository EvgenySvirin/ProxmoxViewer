from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone

from proxmoxer import ProxmoxAPI
from django.shortcuts import render

from django.shortcuts import get_object_or_404, render

from .models import Connection


proxmox = None
proxmox_connection_id = None

def index(request):
    """
    host = "192.168.122.104"
    proxmox = ProxmoxAPI(
    host, backend="https", service="PVE", user="api@pve", password="11111", verify_ssl=False, port=8006
    )

    res = ""
    for node in proxmox.nodes.get():
          print(node)
    res = str(node)
    """
    if request.method == "POST":
    	print("TIS POST")
    	return create_connection(request)
    else:
    	print("TIS NOT POST")
    
    latest_connection_list = Connection.objects.all()
    context = {'latest_connection_list': latest_connection_list}

    return render(request, 'connection/index.html', context) 
    
def detail(request, connection_id):
    connection = get_object_or_404(Connection, pk=connection_id)
    if request.method == "POST":
    	print("TIS POST")
    	return HttpResponseRedirect(reverse('connection:results', args=(connection.id,)))
    else:
    	print("TIS NOT POST")

    return render(request, 'connection/detail.html', {'connection': connection})

def toggle_virt(virt_id): #toggle start/stop of a container or virtual machine
    global proxmox
    for node in proxmox.nodes.get():
    	for vm in proxmox.nodes(node['node']).lxc.get():
        	if int(vm['vmid']) == virt_id:
        		print(vm['status'])
        		toggled_status = "start" if vm['status'] == "stopped" else "stop"
        		post_string = f"nodes/{node['node']}/lxc/{virt_id}/status/{toggled_status}"
        		print(post_string)
        		proxmox.post(post_string)
        		#proxmox.nodes(node['node']).lxc.post("nodes/{l}/lxc/102/status/stop")
        		break
			
def results(request, connection_id): 
    print("FOO")
    if request.method == "POST":
    	if "Refresh" in request.POST.keys():
   	   connect(request, connection_id)
   	   return HttpResponseRedirect(reverse('connection:results', args=(connection_id,)))
    	virt_id = None
    	for k in request.POST.keys():
    		if (k[0] == 's'):
    			virt_id = int(k[1:])
    			break
    	toggle_virt(virt_id)
    	return HttpResponseRedirect(reverse('connection:results', args=(connection_id,)))
    	
    	
    connect(request, connection_id) # ну тут типо нужно правильно следить за соединением, пока так сойдет
    
    global proxmox
    res = "Connection id:"
    global proxmox_connection_id
    res += str(proxmox_connection_id)
    virts = []
    for node in proxmox.nodes.get():
    	for vm in proxmox.nodes(node['node']).lxc.get():
        	virts.append((vm['vmid'], vm['name'], vm['status']))
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



def create_connection(request):
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
     
    return HttpResponseRedirect(reverse('connection:index'))



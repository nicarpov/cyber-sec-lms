let unreg_list = document.getElementById('unregs-list')

function unreg_entry(host){
    return `
    
    `
}

hosts_sock.onmessage = function(event){
    state = JSON.parse(event.data)
    unregs = state['unregistered']
    
}
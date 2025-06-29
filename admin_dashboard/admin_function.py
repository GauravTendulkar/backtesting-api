





def getActivePermissions(data):
    temp = []
    roles = list(data.keys())
    for i in range(len(roles)):
        if data[roles[i]]["active"]:
            
            groups = list(data[roles[i]]["groups"].keys())
            for j in range(len(groups)):
                
                if data[roles[i]]["groups"][groups[j]]["active"]:
                
                    permissions = list(data[roles[i]]["groups"][groups[j]]["permissions"].keys())
                    for k in range(len(permissions)):
                        
                        if data[roles[i]]["groups"][groups[j]]["permissions"][permissions[k]] :
                            
                            if permissions[k] not in temp :

                                temp.append(permissions[k])
    return temp
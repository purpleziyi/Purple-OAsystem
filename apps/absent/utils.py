

def get_responder(request):
    user = request.user
    # 获取审批者
    # 1. 如果是部门leader
    if user.department.leader.uid == user.uid:
        # 1.1. 如果是董事会
        if user.department.name == 'Board':  # 董事会
            responder = None
        else:
            responder = user.department.manager
    # 2. 如果不是部门leader
    else:
        responder = user.department.leader
    return responder
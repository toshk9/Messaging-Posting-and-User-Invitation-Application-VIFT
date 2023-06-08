import time


def get_members(vk_api, group_id, total_count):
    if total_count != "all":
        total_count = int(total_count)
        try:
            members = vk_api.groups.getMembers(group_id=group_id, count=total_count)['items']
        except:
            members = vk_api.groups.getMembers(group_id=group_id)['items']

            offset = 1000
            while offset < total_count:
                members = members + vk_api.groups.getMembers(group_id=group_id, count=1000, offset=offset)['items']
                offset = offset + 1000
                time.sleep(1)
            members = list(set(members))
        return members
    else:
        total_count = vk_api.groups.getMembers(group_id=group_id)['count']
        try:
            members = vk_api.groups.getMembers(group_id=group_id, count=total_count)['items']
        except:
            members = vk_api.groups.getMembers(group_id=group_id)['items']

            offset = 1000
            while offset < total_count:
                members = members + vk_api.groups.getMembers(group_id=group_id, count=1000, offset=offset)['items']
                offset = offset + 1000
                time.sleep(1)
            members = list(set(members))
        return members

def get_friends(vk_api, user_id, total_count):
    if total_count != "all":
        total_count = int(total_count)
        try:
            members = vk_api.friends.get(user_id=user_id, count=total_count)['items']
        except:
            members = vk_api.friends.get(user_id=user_id)['items']

            offset = 1000
            while offset < total_count:
                members = members + vk_api.friends.get(user_id=user_id, count=1000, offset=offset)['items']
                offset = offset + 1000
                time.sleep(1)
            members = list(set(members))
        return members
    else:
        total_count = vk_api.friends.get(user_id=user_id)['count']
        try:
            members = vk_api.friends.get(user_id=user_id, count=total_count)['items']
        except:
            members = vk_api.friends.get(user_id=user_id)['items']

            offset = 1000
            while offset < total_count:
                members = members + vk_api.friends.get(user_id=user_id, count=1000, offset=offset)['items']
                offset = offset + 1000
                time.sleep(1)
            members = list(set(members))
        return members

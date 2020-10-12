class Post:
    def __init__(self, data : dict):
        node = data["node"]
        self.type = node["__typename"]
        self.id = node["id"]
        self.display_url = node["display_url"]
        self.is_video = bool(node["is_video"])
        self.child_posts = []
        if "edge_sidecar_to_children" in node:
            self.child_posts.append(list(map(Post,node["edge_sidecar_to_children"]["edges"])))

class PageInfo:
    def __init__(self, data : dict):
        self.has_next_page = bool(data["has_next_page"])
        self.cursor = data["end_cursor"]
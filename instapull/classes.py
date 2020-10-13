class Post:
    def __init__(self, data : dict):
        node = data["node"]
        self.type = node["__typename"]
        self.id = node["id"]
        self.display_url = node["display_url"]
        self.is_video = bool(node["is_video"])
        self.is_media_collection = self.type == "GraphSidecar"
        self.media = []
        if "edge_sidecar_to_children" in node:
            self.media = list(map(Post,node["edge_sidecar_to_children"]["edges"]))

class PageInfo:
    def __init__(self, data : dict):
        self.has_next_page = bool(data["has_next_page"])
        self.cursor = data["end_cursor"]
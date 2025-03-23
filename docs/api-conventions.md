# Api Conventions

## URL naming:
- Internal API URLs must be named `api_object_action`
    - eg: `api_followrequest_deny` or `api_joinrequest_create`
- this makes them easy to read, and easy to search up
    - ie: you can ctrl+f to find all `api_followrequest` related api views
    - if you had `api_action_follow_request` that becomes much less intuitive to search up

- All API URLs that are compatible with other nodes must be named `node2node_object_action`

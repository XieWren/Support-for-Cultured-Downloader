## To-Do
1) Developer Guide
2) Program termination (NOT 404)
3) More consistent error handling

## Permissions
artist:show # 3. Search artist by ID
pools:show # 2. Search pool by ID
posts:show # 1. Search post by ID
posts:index # 3. Search images with artist tag
users:profile # Check user exists

## Known Errors
code: message [error]
401: Invalid API key [SessionLoader::AuthenticationFailure]
404: That record was not found. [ActiveRecord::RecordNotFound]
403: Access denied [User::PrivilegeError] Insufficient permissions in API Key
403: [NoMethodError] Invalid params sent to endpoint (not encountable normally)
500: [ActiveRecord::RangeError] Large Post ID pivot

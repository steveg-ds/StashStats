## Database Schema

### Tables

#### users
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| email | VARCHAR | User email |
| name | VARCHAR | Display name |

#### stashes
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users |
| name | VARCHAR | Stash name |
| count | INTEGER | Item count |
| yarn_weight | VARCHAR | Weight category |
| created_at | TIMESTAMP | Creation timestamp |

#### projects
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| name | VARCHAR | Project name |
| target_count | INTEGER | Target item count |
| stashes_used | INTEGER | Stashes consumed |

### Indexes
- `idx_stashes_user_id` on stashes(user_id)
- `idx_projects_user_id` on projects(user_id)
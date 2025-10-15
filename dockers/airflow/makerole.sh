#!/usr/bin/env bash
set -euo pipefail

ROLE="${1:-Visitor}"           # 만들 롤 이름 (인자 1로 바꿀 수 있음)
DAG_ID="${2:-etl_daily}"       # DAG 예시 (필요 없으면 빼도 됨)

# 1) 롤 생성 (이미 있으면 에러 없이 패스되게 || true)
# airflow roles create --role "$ROLE" || true
airflow roles create --role "ViewerMinor"

# 2) 퍼미션 동기화 (DAG 리소스 반영)
airflow sync-perm --include-dags

# 3) 전역 리소스 권한 예시 (읽기 전용 대시보드 관람자 느낌)
airflow roles add-perms --role "ViewerMinor" --resource Website       --action can_read
airflow roles add-perms --role "ViewerMinor" --resource Dag           --action can_read
airflow roles add-perms --role "ViewerMinor" --resource DagRun        --action can_read
airflow roles add-perms --role "ViewerMinor" --resource TaskInstance  --action can_read
airflow roles add-perms --role "ViewerMinor" --resource Variable      --action can_read
airflow roles add-perms --role "ViewerMinor" --resource Connection    --action can_read
airflow roles add-perms --role "ViewerMinor" --resource Dataset       --action can_read
airflow roles add-perms --role "ViewerMinor" --resource Pool          --action can_read


airflow roles add-perms -v "ViewerMinor" -r "Browse"           -a menu_access                                        
# airflow roles add-perms -v "ViewerMinor" -r "Cluster Activity"  -a can_read
# airflow roles add-perms -v "ViewerMinor" -r "Cluster Activity"  -a menu_access                               
# airflow roles add-perms -v "ViewerMinor" -r "DAG Code"          -a can_read                                           
airflow roles add-perms -v "ViewerMinor" -r "DAG Dependencies"  -a can_read
airflow roles add-perms -v "ViewerMinor" -r "DAG Dependencies"  -a menu_access                               
# airflow roles add-perms -v "ViewerMinor" -r "DAG Runs"          -a can_read
# airflow roles add-perms -v "ViewerMinor" -r "DAG Runs"          -a menu_access                               
# airflow roles add-perms -v "ViewerMinor" -r "DAG Warnings"      -a can_read                                           
# airflow roles add-perms -v "ViewerMinor" -r "DAGs"              -a can_read
# airflow roles add-perms -v "ViewerMinor" -r "DAGs"              -a menu_access                               
airflow roles add-perms -v "ViewerMinor" -r "Datasets"          -a can_read
airflow roles add-perms -v "ViewerMinor" -r "Datasets"          -a menu_access                               
airflow roles add-perms -v "ViewerMinor" -r "Docs"              -a menu_access                                        
airflow roles add-perms -v "ViewerMinor" -r "Documentation"     -a menu_access                                        
airflow roles add-perms -v "ViewerMinor" -r "ImportError"       -a can_read                                           
airflow roles add-perms -v "ViewerMinor" -r "Jobs"              -a can_read
airflow roles add-perms -v "ViewerMinor" -r "Jobs"              -a menu_access                               
airflow roles add-perms -v "ViewerMinor" -r "My Password"       -a can_edit,can_read                                  
airflow roles add-perms -v "ViewerMinor" -r "My Profile"        -a can_edit,can_read                                  
airflow roles add-perms -v "ViewerMinor" -r "Pools"             -a can_read                                           
airflow roles add-perms -v "ViewerMinor" -r "SLA Misses"        -a can_read
airflow roles add-perms -v "ViewerMinor" -r "SLA Misses"        -a menu_access                               
airflow roles add-perms -v "ViewerMinor" -r "Task Instances"    -a can_read
airflow roles add-perms -v "ViewerMinor" -r "Task Instances"    -a menu_access                               
airflow roles add-perms -v "ViewerMinor" -r "Task Logs"         -a can_read                                           
airflow roles add-perms -v "ViewerMinor" -r "Website"           -a can_read                                           
airflow roles add-perms -v "ViewerMinor" -r "XComs"             -a can_read     



# 3) 전역 리소스 권한 예시 (읽기 전용 대시보드 관람자 느낌)
airflow roles add-perms --role "$ROLE" --resource Website       --action can_read
airflow roles add-perms --role "$ROLE" --resource Dag           --action can_read
airflow roles add-perms --role "$ROLE" --resource DagRun        --action can_read
airflow roles add-perms --role "$ROLE" --resource TaskInstance  --action can_read
airflow roles add-perms --role "$ROLE" --resource Variable      --action can_read
airflow roles add-perms --role "$ROLE" --resource Connection    --action can_read
airflow roles add-perms --role "$ROLE" --resource Dataset       --action can_read
airflow roles add-perms --role "$ROLE" --resource Pool          --action can_read

# 4) 특정 DAG만 보이게/운영하게 (원하면)
airflow roles add-perms --role "$ROLE" --resource Dag --action can_read --dag-id "$DAG_ID"
# 편집/트리거 권한이 필요하면 아래처럼 추가
# airflow roles add-perms --role "$ROLE" --resource Dag --action can_edit --dag-id "$DAG_ID"
# airflow roles add-perms --role "$ROLE" --resource DagRun --action can_create

# (옵션) 잘못 준 권한 회수 예시
# airflow roles del-perms --role "$ROLE" --resource Variable --action can_read

# 5) 결과 확인
airflow roles list -p -o table | awk -v r="$ROLE" '$0 ~ r || NR==1 {print}'

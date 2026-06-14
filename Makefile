backend:
	./scripts/start_backend.sh

frontend:
	./scripts/start_frontend.sh

reset-demo:
	./scripts/reset_demo_data.sh

status:
	git status

commit:
	git add .
	git commit -m "Operationalize local demo workflow"

push:
	git push

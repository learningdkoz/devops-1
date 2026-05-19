{{/* Стандартные хелперы Helm — имена, лейблы и т.п. */}}
{{- define "devops-demo.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "devops-demo.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "devops-demo.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "devops-demo.labels" -}}
app.kubernetes.io/name: {{ include "devops-demo.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end -}}

{{- define "devops-demo.selectorLabels" -}}
app.kubernetes.io/name: {{ include "devops-demo.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

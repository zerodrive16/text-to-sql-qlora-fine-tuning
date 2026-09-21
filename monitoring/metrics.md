# CPU
# Gesamtauslastung
100 - (avg(rate(windows_cpu_time_total{mode="idle"}[1m])) * 100)

# Pro Core
100 - (avg by (core) (rate(windows_cpu_time_total{mode="idle"}[1m])) * 100)

# RAM
# Verfügbarer RAM in GB
windows_memory_available_bytes / 1024 / 1024 / 1024

# RAM-Auslastung in %
100 - ((windows_memory_available_bytes / windows_memory_physical_total_bytes) * 100)

# DISK
# Freier Speicher C: in GB
windows_logical_disk_free_bytes{volume="C:"} / 1024 / 1024 / 1024

# Disk Read/Write Speed (MB/s)
rate(windows_logical_disk_read_bytes_total{volume="C:"}[1m]) / 1024 / 1024
rate(windows_logical_disk_write_bytes_total{volume="C:"}[1m]) / 1024 / 1024

# Netzwerk
# Download (MB/s)
rate(windows_net_bytes_received_total[1m]) / 1024 / 1024

# Upload (MB/s)
rate(windows_net_bytes_sent_total[1m]) / 1024 / 1024

# System
# Uptime in Stunden
(time() - windows_system_system_up_time) / 3600

# Anzahl laufende Prozesse
windows_system_processes

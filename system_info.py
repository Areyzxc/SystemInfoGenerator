import platform
import psutil
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

class SystemInfoCollector:
    """Collects system information and generates reports."""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Collect comprehensive system information."""
        return {
            "timestamp": self.timestamp,
            "system": self._get_system_info(),
            "cpu": self._get_cpu_info(),
            "memory": self._get_memory_info(),
            "disk": self._get_disk_info(),
            "network": self._get_network_info(),
            "boot_time": self._get_boot_time()
        }
    
    def _get_system_info(self) -> Dict[str, str]:
        """Get basic system information."""
        return {
            "system": platform.system(),
            "node_name": platform.node(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version()
        }
    
    def _get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information."""
        return {
            "physical_cores": psutil.cpu_count(logical=False),
            "total_cores": psutil.cpu_count(logical=True),
            "cpu_percent": psutil.cpu_percent(interval=1, percpu=True),
            "cpu_freq": {
                "current": psutil.cpu_freq().current if hasattr(psutil.cpu_freq(), 'current') else "N/A",
                "max": psutil.cpu_freq().max if hasattr(psutil.cpu_freq(), 'max') else "N/A"
            }
        }
    
    def _get_memory_info(self) -> Dict[str, Any]:
        """Get memory information."""
        virtual_mem = psutil.virtual_memory()
        swap_mem = psutil.swap_memory()
        
        return {
            "total_ram": self._format_bytes(virtual_mem.total),
            "available_ram": self._format_bytes(virtual_mem.available),
            "used_ram": self._format_bytes(virtual_mem.used),
            "ram_percent": virtual_mem.percent,
            "total_swap": self._format_bytes(swap_mem.total),
            "used_swap": self._format_bytes(swap_mem.used),
            "swap_percent": swap_mem.percent
        }
    
    def _get_disk_info(self) -> Dict[str, Any]:
        """Get disk/partition information."""
        partitions = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total": self._format_bytes(usage.total),
                    "used": self._format_bytes(usage.used),
                    "free": self._format_bytes(usage.free),
                    "percent": usage.percent
                })
            except Exception:
                continue
                
        return {"partitions": partitions}
    
    def _get_network_info(self) -> Dict[str, Any]:
        """Get network interface information."""
        interfaces = {}
        for interface, addrs in psutil.net_if_addrs().items():
            interfaces[interface] = []
            for addr in addrs:
                interfaces[interface].append({
                    "family": str(addr.family),
                    "address": addr.address,
                    "netmask": addr.netmask if addr.netmask else "N/A",
                    "broadcast": addr.broadcast if addr.broadcast else "N/A"
                })
        
        return {
            "interfaces": interfaces,
            "io_counters": {
                "bytes_sent": self._format_bytes(psutil.net_io_counters().bytes_sent),
                "bytes_recv": self._format_bytes(psutil.net_io_counters().bytes_recv),
                "packets_sent": psutil.net_io_counters().packets_sent,
                "packets_recv": psutil.net_io_counters().packets_recv
            }
        }
    
    def _get_boot_time(self) -> str:
        """Get system boot time."""
        return datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def _format_bytes(bytes_num: int) -> str:
        """Format bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_num < 1024.0:
                return f"{bytes_num:.2f} {unit}"
            bytes_num /= 1024.0
        return f"{bytes_num:.2f} PB"


class ReportGenerator:
    """Generates different types of reports from system information."""
    
    @staticmethod
    def generate_text_report(sys_info: Dict[str, Any]) -> str:
        """Generate a human-readable text report."""
        report = []
        report.append("=" * 50)
        report.append(f"SYSTEM INFORMATION REPORT - {sys_info['timestamp']}")
        report.append("=" * 50)
        
        # System Information
        report.append("\nSYSTEM INFORMATION")
        report.append("-" * 30)
        for key, value in sys_info['system'].items():
            report.append(f"{key.replace('_', ' ').title()}: {value}")
        
        # CPU Information
        report.append("\nCPU INFORMATION")
        report.append("-" * 30)
        cpu = sys_info['cpu']
        report.append(f"Physical Cores: {cpu['physical_cores']}")
        report.append(f"Total Cores: {cpu['total_cores']}")
        report.append(f"CPU Usage: {sum(cpu['cpu_percent'])/len(cpu['cpu_percent']):.1f}%")
        report.append(f"CPU Frequency: {cpu['cpu_freq']['current']} MHz")
        
        # Memory Information
        report.append("\nMEMORY INFORMATION")
        report.append("-" * 30)
        mem = sys_info['memory']
        report.append(f"Total RAM: {mem['total_ram']}")
        report.append(f"Available RAM: {mem['available_ram']}")
        report.append(f"Used RAM: {mem['used_ram']} ({mem['ram_percent']}%)")
        report.append(f"Total Swap: {mem['total_swap']}")
        report.append(f"Used Swap: {mem['used_swap']} ({mem['swap_percent']}%)")
        
        # Disk Information
        report.append("\nDISK INFORMATION")
        report.append("-" * 30)
        for partition in sys_info['disk']['partitions']:
            report.append(f"\nDevice: {partition['device']} ({partition['fstype']}) mounted on {partition['mountpoint']}")
            report.append(f"  Total: {partition['total']}")
            report.append(f"  Used: {partition['used']} ({partition['percent']}%)")
            report.append(f"  Free: {partition['free']}")
        
        # Network Information
        report.append("\nNETWORK INFORMATION")
        report.append("-" * 30)
        report.append("Network Interfaces:")
        for interface, addrs in sys_info['network']['interfaces'].items():
            report.append(f"  {interface}:")
            for addr in addrs:
                if ':' not in addr['address']:  # Skip IPv6 for brevity
                    report.append(f"    {addr['family']}: {addr['address']}")
        
        net_io = sys_info['network']['io_counters']
        report.append(f"\nNetwork I/O:")
        report.append(f"  Bytes Sent: {net_io['bytes_sent']}")
        report.append(f"  Bytes Received: {net_io['bytes_recv']}")
        
        # Boot Time
        report.append("\nSYSTEM UPTIME")
        report.append("-" * 30)
        report.append(f"System Boot Time: {sys_info['boot_time']}")
        
        return "\n".join(report)
    
    @staticmethod
    def generate_html_report(sys_info: Dict[str, Any]) -> str:
        """Generate an HTML report."""
        # Format disk rows
        disk_rows = []
        for partition in sys_info['disk']['partitions']:
            disk_rows.append(
                f"<tr>"
                f"<td>{partition['device']}</td>"
                f"<td>{partition['mountpoint']}</td>"
                f"<td>{partition['fstype']}</td>"
                f"<td>{partition['total']}</td>"
                f"<td>{partition['used']}</td>"
                f"<td>{partition['free']}</td>"
                f"<td>{partition['percent']}%</td>"
                f"</tr>"
            )
        
        # Format network interfaces
        network_interfaces = []
        for interface, addrs in sys_info['network']['interfaces'].items():
            network_interfaces.append(f"<h4>{interface}</h4><ul>")
            for addr in addrs:
                if ':' not in addr['address']:  # Skip IPv6 for brevity
                    network_interfaces.append(f"<li><strong>{addr['family']}:</strong> {addr['address']}")
                    if addr['netmask'] != 'N/A':
                        network_interfaces.append(f" (Netmask: {addr['netmask']})")
                    if addr['broadcast'] != 'N/A':
                        network_interfaces.append(f" (Broadcast: {addr['broadcast']})")
                    network_interfaces.append("</li>")
            network_interfaces.append("</ul>")
        
        # Calculate average CPU usage
        cpu_percent_avg = sum(sys_info['cpu']['cpu_percent']) / len(sys_info['cpu']['cpu_percent'])
        
        # Format the HTML content
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>System Information Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: #333; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ border-bottom: 2px solid #333; padding-bottom: 5px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
        .card {{ background: #f4f4f4; padding: 15px; border-radius: 5px; }}
        .card h3 {{ margin-top: 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
        .footer {{ margin-top: 30px; text-align: center; font-size: 0.9em; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>System Information Report</h1>
            <p>Generated on: {sys_info['timestamp']}</p>
        </div>
        
        <div class="section">
            <h2>System Information</h2>
            <div class="grid">
                <div class="card">
                    <h3>System</h3>
                    <p><strong>OS:</strong> {sys_info['system']['system']} {sys_info['system']['release']}</p>
                    <p><strong>Version:</strong> {sys_info['system']['version']}</p>
                    <p><strong>Node Name:</strong> {sys_info['system']['node_name']}</p>
                    <p><strong>Machine:</strong> {sys_info['system']['machine']}</p>
                    <p><strong>Processor:</strong> {sys_info['system']['processor']}</p>
                    <p><strong>Python Version:</strong> {sys_info['system']['python_version']}</p>
                </div>
                
                <div class="card">
                    <h3>CPU</h3>
                    <p><strong>Physical Cores:</strong> {sys_info['cpu']['physical_cores']}</p>
                    <p><strong>Total Cores:</strong> {sys_info['cpu']['total_cores']}</p>
                    <p><strong>CPU Usage:</strong> {cpu_percent_avg:.1f}%</p>
                    <p><strong>Current Frequency:</strong> {sys_info['cpu']['cpu_freq']['current']} MHz</p>
                    <p><strong>Max Frequency:</strong> {sys_info['cpu']['cpu_freq']['max']} MHz</p>
                </div>
                
                <div class="card">
                    <h3>Memory</h3>
                    <p><strong>Total RAM:</strong> {sys_info['memory']['total_ram']}</p>
                    <p><strong>Available RAM:</strong> {sys_info['memory']['available_ram']} ({sys_info['memory']['ram_percent']}% used)</p>
                    <p><strong>Total Swap:</strong> {sys_info['memory']['total_swap']}</p>
                    <p><strong>Used Swap:</strong> {sys_info['memory']['used_swap']} ({sys_info['memory']['swap_percent']}% used)</p>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Disk Information</h2>
            <table>
                <tr>
                    <th>Device</th>
                    <th>Mount Point</th>
                    <th>File System</th>
                    <th>Total</th>
                    <th>Used</th>
                    <th>Free</th>
                    <th>Use %</th>
                </tr>
                {''.join(disk_rows)}
            </table>
        </div>
        
        <div class="section">
            <h2>Network Information</h2>
            <h3>Network Interfaces</h3>
            {''.join(network_interfaces)}
            
            <h3>Network I/O</h3>
            <p><strong>Bytes Sent:</strong> {sys_info['network']['io_counters']['bytes_sent']}</p>
            <p><strong>Bytes Received:</strong> {sys_info['network']['io_counters']['bytes_recv']}</p>
            <p><strong>Packets Sent:</strong> {sys_info['network']['io_counters']['packets_sent']:,}</p>
            <p><strong>Packets Received:</strong> {sys_info['network']['io_counters']['packets_recv']:,}</p>
        </div>
        
        <div class="section">
            <h2>System Uptime</h2>
            <p><strong>System Boot Time:</strong> {sys_info['boot_time']}</p>
            <p><strong>Report Generated:</strong> {sys_info['timestamp']}</p>
        </div>
        
        <div class="footer">
            <p>Generated by SystemInfoGenerator | {sys_info['timestamp']}</p>
        </div>
    </div>
</body>
</html>"""
    
    @staticmethod
    def generate_json_report(sys_info: Dict[str, Any]) -> str:
        """Generate a JSON report."""
        return json.dumps(sys_info, indent=4)
        
    @staticmethod
    def generate_csv_report(sys_info: Dict[str, Any]) -> str:
        """Generate a CSV report."""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Category', 'Metric', 'Value'])
        
        # System Information
        writer.writerow(['System', 'OS', f"{sys_info['system']['system']} {sys_info['system']['release']}"])
        writer.writerow(['System', 'Node Name', sys_info['system']['node_name']])
        writer.writerow(['System', 'Version', sys_info['system']['version']])
        writer.writerow(['System', 'Machine', sys_info['system']['machine']])
        writer.writerow(['System', 'Processor', sys_info['system']['processor']])
        writer.writerow(['System', 'Python Version', sys_info['system']['python_version']])
        
        # CPU Information
        writer.writerow(['CPU', 'Physical Cores', sys_info['cpu']['physical_cores']])
        writer.writerow(['CPU', 'Total Cores', sys_info['cpu']['total_cores']])
        writer.writerow(['CPU', 'Average Usage', f"{sum(sys_info['cpu']['cpu_percent']) / len(sys_info['cpu']['cpu_percent']):.1f}%"])
        writer.writerow(['CPU', 'Current Frequency', f"{sys_info['cpu']['cpu_freq']['current']} MHz"])
        writer.writerow(['CPU', 'Max Frequency', f"{sys_info['cpu']['cpu_freq']['max']} MHz"])
        
        # Memory Information
        writer.writerow(['Memory', 'Total RAM', sys_info['memory']['total_ram']])
        writer.writerow(['Memory', 'Available RAM', sys_info['memory']['available_ram']])
        writer.writerow(['Memory', 'Used RAM', f"{sys_info['memory']['used_ram']} ({sys_info['memory']['ram_percent']}%)"])
        writer.writerow(['Memory', 'Total Swap', sys_info['memory']['total_swap']])
        writer.writerow(['Memory', 'Used Swap', f"{sys_info['memory']['used_swap']} ({sys_info['memory']['swap_percent']}%)"])
        
        # Disk Information
        for i, partition in enumerate(sys_info['disk']['partitions']):
            writer.writerow([
                'Disk' if i == 0 else '',
                partition['mountpoint'],
                f"{partition['used']} / {partition['total']} ({partition['percent']}% used)"
            ])
        
        # Network Information
        for interface, addrs in sys_info['network']['interfaces'].items():
            for addr in addrs:
                if ':' not in addr['address']:  # Skip IPv6 for brevity
                    writer.writerow(['Network', f"{interface} ({addr['family']})", addr['address']])
        
        # Network I/O
        io = sys_info['network']['io_counters']
        writer.writerow(['Network', 'Bytes Sent', io['bytes_sent']])
        writer.writerow(['Network', 'Bytes Received', io['bytes_recv']])
        writer.writerow(['Network', 'Packets Sent', io['packets_sent']])
        writer.writerow(['Network', 'Packets Received', io['packets_recv']])
        
        # System Uptime
        writer.writerow(['System', 'Boot Time', sys_info['boot_time']])
        writer.writerow(['System', 'Report Generated', sys_info['timestamp']])
        
        return output.getvalue()
    
    @staticmethod
    def generate_pdf_report(sys_info: Dict[str, Any]) -> bytes:
        """Generate a PDF report."""
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        import tempfile
        import os
        
        # Create a temporary file for the PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            pdf_path = tmp.name
        
        # Create PDF document
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            alignment=1  # Center aligned
        )
        elements.append(Paragraph("System Information Report", title_style))
        
        # Subtitle
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=20,
            alignment=1  # Center aligned
        )
        elements.append(Paragraph(f"Generated on: {sys_info['timestamp']}", subtitle_style))
        
        # System Information
        elements.append(Paragraph("System Information", styles['Heading2']))
        
        sys_data = [
            ['OS', f"{sys_info['system']['system']} {sys_info['system']['release']}"],
            ['Node Name', sys_info['system']['node_name']],
            ['Version', sys_info['system']['version']],
            ['Machine', sys_info['system']['machine']],
            ['Processor', sys_info['system']['processor']],
            ['Python Version', sys_info['system']['python_version']]
        ]
        
        sys_table = Table(sys_data, colWidths=[doc.width/3.0]*2)
        sys_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(sys_table)
        elements.append(Spacer(1, 20))
        
        # CPU Information
        elements.append(Paragraph("CPU Information", styles['Heading2']))
        
        cpu_percent_avg = sum(sys_info['cpu']['cpu_percent']) / len(sys_info['cpu']['cpu_percent'])
        cpu_data = [
            ['Physical Cores', sys_info['cpu']['physical_cores']],
            ['Total Cores', sys_info['cpu']['total_cores']],
            ['Average Usage', f"{cpu_percent_avg:.1f}%"],
            ['Current Frequency', f"{sys_info['cpu']['cpu_freq']['current']} MHz"],
            ['Max Frequency', f"{sys_info['cpu']['cpu_freq']['max']} MHz"]
        ]
        
        cpu_table = Table(cpu_data, colWidths=[doc.width/3.0]*2)
        cpu_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(cpu_table)
        elements.append(Spacer(1, 20))
        
        # Memory Information
        elements.append(Paragraph("Memory Information", styles['Heading2']))
        
        mem_data = [
            ['Total RAM', sys_info['memory']['total_ram']],
            ['Available RAM', sys_info['memory']['available_ram']],
            ['Used RAM', f"{sys_info['memory']['used_ram']} ({sys_info['memory']['ram_percent']}%)"],
            ['Total Swap', sys_info['memory']['total_swap']],
            ['Used Swap', f"{sys_info['memory']['used_swap']} ({sys_info['memory']['swap_percent']}%)"]
        ]
        
        mem_table = Table(mem_data, colWidths=[doc.width/3.0]*2)
        mem_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(mem_table)
        elements.append(Spacer(1, 20))
        
        # Disk Information
        if sys_info['disk']['partitions']:
            elements.append(Paragraph("Disk Information", styles['Heading2']))
            
            disk_headers = ['Mount Point', 'File System', 'Total', 'Used', 'Free', 'Use %']
            disk_data = [disk_headers]
            
            for partition in sys_info['disk']['partitions']:
                disk_data.append([
                    partition['mountpoint'],
                    partition['fstype'],
                    partition['total'],
                    partition['used'],
                    partition['free'],
                    f"{partition['percent']}%"
                ])
            
            # Calculate column widths (adjust as needed)
            col_widths = [
                doc.width * 0.2,  # Mount Point
                doc.width * 0.15,  # File System
                doc.width * 0.15,  # Total
                doc.width * 0.15,  # Used
                doc.width * 0.15,  # Free
                doc.width * 0.1,   # Use %
            ]
            
            disk_table = Table(disk_data, colWidths=col_widths)
            disk_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(disk_table)
            elements.append(Spacer(1, 20))
        
        # Network Information
        elements.append(Paragraph("Network Information", styles['Heading2']))
        
        # Network Interfaces
        elements.append(Paragraph("Network Interfaces", styles['Heading3']))
        
        net_data = [['Interface', 'Family', 'Address', 'Netmask', 'Broadcast']]
        
        for interface, addrs in sys_info['network']['interfaces'].items():
            for addr in addrs:
                net_data.append([
                    interface,
                    addr['family'],
                    addr['address'],
                    addr.get('netmask', 'N/A'),
                    addr.get('broadcast', 'N/A')
                ])
        
        # Calculate column widths (adjust as needed)
        net_col_widths = [
            doc.width * 0.15,  # Interface
            doc.width * 0.1,   # Family
            doc.width * 0.25,  # Address
            doc.width * 0.25,  # Netmask
            doc.width * 0.15,  # Broadcast
        ]
        
        net_table = Table(net_data, colWidths=net_col_widths)
        net_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(net_table)
        elements.append(Spacer(1, 20))
        
        # Network I/O
        elements.append(Paragraph("Network I/O Counters", styles['Heading3']))
        
        io_data = [
            ['Bytes Sent', sys_info['network']['io_counters']['bytes_sent']],
            ['Bytes Received', sys_info['network']['io_counters']['bytes_recv']],
            ['Packets Sent', f"{sys_info['network']['io_counters']['packets_sent']:,}"],
            ['Packets Received', f"{sys_info['network']['io_counters']['packets_recv']:,}"]
        ]
        
        io_table = Table(io_data, colWidths=[doc.width/3.0]*2)
        io_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(io_table)
        elements.append(Spacer(1, 20))
        
        # System Uptime
        elements.append(Paragraph("System Uptime", styles['Heading2']))
        
        uptime_data = [
            ['Boot Time', sys_info['boot_time']],
            ['Report Generated', sys_info['timestamp']]
        ]
        
        uptime_table = Table(uptime_data, colWidths=[doc.width/3.0]*2)
        uptime_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(uptime_table)
        
        # Footer
        elements.append(Spacer(1, 20))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            spaceBefore=20,
            alignment=1  # Center aligned
        )
        elements.append(Paragraph("Generated by SystemInfoGenerator", footer_style))
        
        # Build the PDF
        doc.build(elements)
        
        # Read the generated PDF
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
        
        # Clean up the temporary file
        try:
            os.unlink(pdf_path)
        except:
            pass
        
        return pdf_data
        
    @staticmethod
    def generate_gui_report(sys_info: Dict[str, Any]):
        """Generate a GUI report using tkinter."""
        try:
            import tkinter as tk
            from tkinter import ttk
            from tkinter.scrolledtext import ScrolledText
            import webbrowser
            
            class SystemInfoGUI:
                def __init__(self, sys_info):
                    self.sys_info = sys_info
                    self.root = tk.Tk()
                    self.root.title("System Information Report")
                    self.root.geometry("900x700")
                    self.root.minsize(800, 600)
                    
                    # Configure style
                    style = ttk.Style()
                    style.configure("TNotebook.Tab", padding=[10, 5], font=('Arial', 10, 'bold'))
                    style.configure("Title.TLabel", font=('Arial', 16, 'bold'))
                    style.configure("Subtitle.TLabel", font=('Arial', 12, 'bold'))
                    
                    # Create main container
                    main_frame = ttk.Frame(self.root, padding="10")
                    main_frame.pack(fill=tk.BOTH, expand=True)
                    
                    # Add title
                    title = ttk.Label(
                        main_frame, 
                        text="System Information Report", 
                        style="Title.TLabel"
                    )
                    title.pack(pady=(0, 10))
                    
                    # Add timestamp
                    timestamp = ttk.Label(
                        main_frame,
                        text=f"Generated on: {sys_info['timestamp']}"
                    )
                    timestamp.pack(pady=(0, 15))
                    
                    # Create notebook for tabs
                    notebook = ttk.Notebook(main_frame)
                    notebook.pack(fill=tk.BOTH, expand=True)
                    
                    # System Info Tab
                    self._create_system_tab(notebook)
                    
                    # CPU Info Tab
                    self._create_cpu_tab(notebook)
                    
                    # Memory Info Tab
                    self._create_memory_tab(notebook)
                    
                    # Disk Info Tab
                    self._create_disk_tab(notebook)
                    
                    # Network Info Tab
                    self._create_network_tab(notebook)

                    # About Us Tab
                    self._create_about_tab(notebook)
                    
                    # Add export buttons
                    btn_frame = ttk.Frame(main_frame)
                    btn_frame.pack(fill=tk.X, pady=(10, 0))
                    
                    ttk.Button(
                        btn_frame, 
                        text="Export as Text", 
                        command=lambda: self._export_report('text')
                    ).pack(side=tk.LEFT, padx=2)
                    
                    ttk.Button(
                        btn_frame, 
                        text="Export as HTML", 
                        command=lambda: self._export_report('html')
                    ).pack(side=tk.LEFT, padx=2)
                    
                    ttk.Button(
                        btn_frame, 
                        text="Export as JSON", 
                        command=lambda: self._export_report('json')
                    ).pack(side=tk.LEFT, padx=2)
                    
                    ttk.Button(
                        btn_frame,
                        text="Export as CSV",
                        command=lambda: self._export_report('csv')
                    ).pack(side=tk.LEFT, padx=2)
                    
                    ttk.Button(
                        btn_frame,
                        text="Export as PDF",
                        command=lambda: self._export_report('pdf')
                    ).pack(side=tk.LEFT, padx=2)
                    
                    # Center the window
                    self.root.eval('tk::PlaceWindow . center')
                    
                def _create_system_tab(self, notebook):
                    frame = ttk.Frame(notebook, padding=10)
                    notebook.add(frame, text="System")
                    
                    # System Info
                    sys_frame = ttk.LabelFrame(frame, text="System Information", padding=10)
                    sys_frame.pack(fill=tk.X, pady=5)
                    
                    sys_info = self.sys_info['system']
                    self._add_info_row(sys_frame, "OS:", f"{sys_info['system']} {sys_info['release']}")
                    self._add_info_row(sys_frame, "Version:", sys_info['version'])
                    self._add_info_row(sys_frame, "Node Name:", sys_info['node_name'])
                    self._add_info_row(sys_frame, "Machine:", sys_info['machine'])
                    self._add_info_row(sys_frame, "Processor:", sys_info['processor'])
                    self._add_info_row(sys_frame, "Python Version:", sys_info['python_version'])
                    
                    # Boot Time
                    boot_frame = ttk.LabelFrame(frame, text="System Uptime", padding=10)
                    boot_frame.pack(fill=tk.X, pady=5)
                    
                    self._add_info_row(boot_frame, "Boot Time:", self.sys_info['boot_time'])
                    self._add_info_row(boot_frame, "Report Generated:", self.sys_info['timestamp'])
                
                def _create_cpu_tab(self, notebook):
                    frame = ttk.Frame(notebook, padding=10)
                    notebook.add(frame, text="CPU")
                    
                    cpu = self.sys_info['cpu']
                    
                    # CPU Info
                    info_frame = ttk.LabelFrame(frame, text="CPU Information", padding=10)
                    info_frame.pack(fill=tk.X, pady=5)
                    
                    self._add_info_row(info_frame, "Physical Cores:", cpu['physical_cores'])
                    self._add_info_row(info_frame, "Total Cores:", cpu['total_cores'])
                    self._add_info_row(info_frame, "CPU Usage:", f"{sum(cpu['cpu_percent'])/len(cpu['cpu_percent']):.1f}%")
                    self._add_info_row(info_frame, "Current Frequency:", f"{cpu['cpu_freq']['current']} MHz")
                    self._add_info_row(info_frame, "Max Frequency:", f"{cpu['cpu_freq']['max']} MHz")
                    
                    # CPU Usage per Core
                    usage_frame = ttk.LabelFrame(frame, text="CPU Usage per Core", padding=10)
                    usage_frame.pack(fill=tk.BOTH, expand=True, pady=5)
                    
                    for i, percent in enumerate(cpu['cpu_percent']):
                        self._add_progress_row(usage_frame, f"Core {i + 1}:", percent)
                
                def _create_memory_tab(self, notebook):
                    frame = ttk.Frame(notebook, padding=10)
                    notebook.add(frame, text="Memory")
                    
                    mem = self.sys_info['memory']
                    
                    # RAM Info
                    ram_frame = ttk.LabelFrame(frame, text="RAM", padding=10)
                    ram_frame.pack(fill=tk.X, pady=5)
                    
                    self._add_progress_row(ram_frame, "RAM Usage:", mem['ram_percent'], 
                                         f"{mem['used_ram']} / {mem['total_ram']}")
                    
                    # Swap Info
                    swap_frame = ttk.LabelFrame(frame, text="Swap Memory", padding=10)
                    swap_frame.pack(fill=tk.X, pady=5)
                    
                    self._add_progress_row(swap_frame, "Swap Usage:", mem['swap_percent'],
                                         f"{mem['used_swap']} / {mem['total_swap']}")
                
                def _create_disk_tab(self, notebook):
                    frame = ttk.Frame(notebook, padding=10)
                    notebook.add(frame, text="Disks")
                    
                    # Create Treeview for disk info
                    columns = ('device', 'mountpoint', 'fstype', 'total', 'used', 'free', 'percent')
                    tree = ttk.Treeview(frame, columns=columns, show='headings', selectmode='browse')
                    
                    # Define headings
                    tree.heading('device', text='Device')
                    tree.heading('mountpoint', text='Mount Point')
                    tree.heading('fstype', text='File System')
                    tree.heading('total', text='Total')
                    tree.heading('used', text='Used')
                    tree.heading('free', text='Free')
                    tree.heading('percent', text='Use %')
                    
                    # Set column widths
                    tree.column('device', width=100, anchor='w')
                    tree.column('mountpoint', width=150, anchor='w')
                    tree.column('fstype', width=80, anchor='w')
                    tree.column('total', width=100, anchor='e')
                    tree.column('used', width=100, anchor='e')
                    tree.column('free', width=100, anchor='e')
                    tree.column('percent', width=70, anchor='e')
                    
                    # Add scrollbar
                    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
                    tree.configure(yscroll=scrollbar.set)
                    
                    # Pack the tree and scrollbar
                    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                    
                    # Add data to the tree
                    for partition in self.sys_info['disk']['partitions']:
                        tree.insert('', tk.END, values=(
                            partition['device'],
                            partition['mountpoint'],
                            partition['fstype'],
                            partition['total'],
                            partition['used'],
                            partition['free'],
                            f"{partition['percent']}%"
                        ))
                
                def _create_network_tab(self, notebook):
                    frame = ttk.Frame(notebook, padding=10)
                    notebook.add(frame, text="Network")
                    
                    # Network Interfaces
                    if_frame = ttk.LabelFrame(frame, text="Network Interfaces", padding=10)
                    if_frame.pack(fill=tk.X, pady=5)
                    
                    for interface, addrs in self.sys_info['network']['interfaces'].items():
                        if_frame_lbl = ttk.Label(if_frame, text=f"{interface}:", font=('Arial', 10, 'bold'))
                        if_frame_lbl.pack(anchor='w', pady=(5, 2))
                        
                        for addr in addrs:
                            if ':' not in addr['address']:  # Skip IPv6 for brevity
                                addr_str = f"{addr['family']}: {addr['address']}"
                                if addr['netmask'] != 'N/A':
                                    addr_str += f" (Netmask: {addr['netmask']})"
                                if addr['broadcast'] != 'N/A':
                                    addr_str += f" (Broadcast: {addr['broadcast']})"
                                ttk.Label(if_frame, text=addr_str).pack(anchor='w', padx=20)
                    
                    # Network I/O
                    io_frame = ttk.LabelFrame(frame, text="Network I/O Counters", padding=10)
                    io_frame.pack(fill=tk.X, pady=5)
                    
                    io = self.sys_info['network']['io_counters']
                    self._add_info_row(io_frame, "Bytes Sent:", io['bytes_sent'])
                    self._add_info_row(io_frame, "Bytes Received:", io['bytes_recv'])
                    self._add_info_row(io_frame, "Packets Sent:", f"{io['packets_sent']:,}")
                    self._add_info_row(io_frame, "Packets Received:", f"{io['packets_recv']:,}")

                def _create_about_tab(self, notebook):
                    """Create the About Us tab with project information."""
                    frame = ttk.Frame(notebook, padding=20)
                    notebook.add(frame, text="About Us")
                    
                    # Project Title
                    title_font = ('Arial', 16, 'bold')
                    header_font = ('Arial', 12, 'bold')
                    text_font = ('Arial', 10)
                    
                    ttk.Label(
                        frame, 
                        text="System Information Tool", 
                        font=title_font,
                        justify='center'
                    ).pack(pady=(0, 20))
                    
                    # Project Description
                    desc_frame = ttk.LabelFrame(frame, text="Project Description", padding=10)
                    desc_frame.pack(fill='x', pady=5)
                    
                    description = (
                        "This tool provides comprehensive system information and monitoring capabilities. "
                        "It was developed as part of the System Administration and Maintenance course project for the Finals."
                    )
                    
                    ttk.Label(
                        desc_frame, 
                        text=description,
                        font=text_font,
                        wraplength=600,
                        justify='left'
                    ).pack(anchor='w')
                    
                    # Team Members
                    team_frame = ttk.LabelFrame(frame, text="Development Team", padding=10)
                    team_frame.pack(fill='x', pady=5)
                    
                    team_members = [
                        "Belza, John Jaylyn I. - Role/Contribution",
                        "Constantino, Alvin Jr. B. - Role/Contribution",
                        "Sabangan, Ybo T. - Role/Contribution",
                        "Santiago, James Aries G. - Role/Contribution",
                        "Silvestre, Jesse Lei C.  - Role/Contribution"
                    ]
                    
                    for member in team_members:
                        ttk.Label(
                            team_frame,
                            text=f"• {member}",
                            font=text_font,
                            justify='left'
                        ).pack(anchor='w', padx=10, pady=2)
                    
                    # Course Information
                    course_frame = ttk.LabelFrame(frame, text="Course Information", padding=10)
                    course_frame.pack(fill='x', pady=5)
                    
                    course_info = [
                        "Course: System Administration and Maintenance",
                        "Instructor: Prof. Joane Pearl G. Carandang",
                        "Institution: Pateros Technological College",
                        "Year: 2025",
                        "Version: 1.0"
                    ]
                    
                    for info in course_info:
                        ttk.Label(
                            course_frame,
                            text=info,
                            font=text_font,
                            justify='left'
                        ).pack(anchor='w', padx=10, pady=2)
                        
                def _add_info_row(self, parent, label, value):
                    """Helper method to add a label and value to a frame."""
                    frame = ttk.Frame(parent)
                    frame.pack(fill=tk.X, pady=2)
                    
                    lbl = ttk.Label(frame, text=label, width=20, anchor='w')
                    lbl.pack(side=tk.LEFT)
                    
                    val = ttk.Label(frame, text=value, anchor='w')
                    val.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                def _add_progress_row(self, parent, label, percent, text=None):
                    """Helper method to add a progress bar row."""
                    frame = ttk.Frame(parent)
                    frame.pack(fill=tk.X, pady=2)
                    
                    lbl = ttk.Label(frame, text=label, width=15, anchor='w')
                    lbl.pack(side=tk.LEFT)
                    
                    style = ttk.Style()
                    style_name = f"{label.replace(' ', '').lower()}.Horizontal.TProgressbar"
                    style.configure(style_name, thickness=20)
                    
                    progress = ttk.Progressbar(
                        frame, 
                        orient=tk.HORIZONTAL, 
                        length=200, 
                        mode='determinate',
                        style=style_name
                    )
                    progress['value'] = percent
                    progress.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                    
                    if text:
                        ttk.Label(frame, text=text, width=30).pack(side=tk.LEFT, padx=5)
                    else:
                        ttk.Label(frame, text=f"{percent:.1f}%").pack(side=tk.LEFT, padx=5)
                
                def _export_report(self, format_type):
                    """Export the report in the specified format."""
                    import os
                    import tempfile
                    import webbrowser
                    from tkinter import messagebox
                    
                    try:
                        if format_type == 'text':
                            content = ReportGenerator.generate_text_report(self.sys_info)
                            ext = '.txt'
                            mode = 'w'
                            encoding = 'utf-8'
                        elif format_type == 'html':
                            content = ReportGenerator.generate_html_report(self.sys_info)
                            ext = '.html'
                            mode = 'w'
                            encoding = 'utf-8'
                        elif format_type == 'json':
                            content = ReportGenerator.generate_json_report(self.sys_info)
                            ext = '.json'
                            mode = 'w'
                            encoding = 'utf-8'
                        elif format_type == 'csv':
                            content = ReportGenerator.generate_csv_report(self.sys_info)
                            ext = '.csv'
                            mode = 'w'
                            encoding = 'utf-8'
                        elif format_type == 'pdf':
                            content = ReportGenerator.generate_pdf_report(self.sys_info)
                            ext = '.pdf'
                            mode = 'wb'
                            encoding = None
                        else:
                            return
                        
                        # Save to a temporary file
                        with tempfile.NamedTemporaryFile(suffix=ext, delete=False, mode=mode, encoding=encoding) as f:
                            if format_type == 'pdf':
                                f.write(content)
                            else:
                                f.write(content)
                            temp_path = f.name
                        
                        # Open the file with the default application
                        webbrowser.open(f'file://{os.path.abspath(temp_path)}')
                        
                        # Show success message for CSV
                        if format_type == 'csv':
                            messagebox.showinfo(
                                "Export Successful",
                                f"CSV report saved to:\n{os.path.abspath(temp_path)}\n\n"
                                "You can open this file in any spreadsheet application "
                                "like Microsoft Excel or Google Sheets."
                            )
                            
                    except Exception as e:
                        messagebox.showerror(
                            "Export Error",
                            f"Failed to export {format_type.upper()} report.\n\nError: {str(e)}"
                        )
                
                def run(self):
                    """Run the GUI main loop."""
                    self.root.mainloop()
            
            # Create and run the GUI
            gui = SystemInfoGUI(sys_info)
            gui.run()
            
        except ImportError as e:
            print(f"Error: {e}. GUI features require tkinter to be installed.")
            print("On Ubuntu/Debian, install it with: sudo apt-get install python3-tk")
            print("On Windows/macOS, it should be included with Python by default.")
            return "GUI not available"


def main():
    """Main function to demonstrate the functionality."""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description='Generate system information reports.')
    parser.add_argument('--output', '-o', type=str, default='gui',
                        choices=['text', 'html', 'json', 'csv', 'pdf', 'gui'],
                        help='Output format (default: gui)')
    parser.add_argument('--file', '-f', type=str, 
                        help='Output file path (default: print to console or show GUI)')
    
    args = parser.parse_args()
    
    # Collect system information
    print("Collecting system information...")
    collector = SystemInfoCollector()
    sys_info = collector.get_system_info()
    
    # Handle GUI mode
    if args.output == 'gui':
        ReportGenerator.generate_gui_report(sys_info)
        return
    
    # Generate the requested report
    if args.output == 'html':
        report = ReportGenerator.generate_html_report(sys_info)
        ext = '.html'
    elif args.output == 'json':
        report = ReportGenerator.generate_json_report(sys_info)
        ext = '.json'
    elif args.output == 'csv':
        report = ReportGenerator.generate_csv_report(sys_info)
        ext = '.csv'
    elif args.output == 'pdf':
        report = ReportGenerator.generate_pdf_report(sys_info)
        ext = '.pdf'
    else:  # text
        report = ReportGenerator.generate_text_report(sys_info)
        ext = '.txt'
    
    # Output the report
    if args.file:
        output_file = args.file
        if not output_file.endswith(ext):
            output_file += ext
    else:
        output_file = f"system_report_{int(time.time())}{ext}"
    
    # Handle binary vs text output
    if args.output == 'pdf':
        with open(output_file, 'wb') as f:
            f.write(report)
    else:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
    
    print(f"Report generated successfully: {os.path.abspath(output_file)}")
    
    # Open the file if it's HTML or PDF
    if args.output in ['html', 'pdf']:
        try:
            if os.name == 'nt':  # Windows
                os.startfile(os.path.abspath(output_file))
            else:  # macOS and Linux
                import webbrowser
                webbrowser.open(f'file://{os.path.abspath(output_file)}')
        except Exception as e:
            print(f"Could not open the file automatically: {e}")
            print(f"Please open the file manually: {os.path.abspath(output_file)}")
    elif args.output == 'csv':
        print(f"CSV report saved to: {os.path.abspath(output_file)}")
        print("You can open this file in any spreadsheet application like Microsoft Excel or Google Sheets.")


if __name__ == "__main__":
    main()

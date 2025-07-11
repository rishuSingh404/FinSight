import time
import logging
import psutil
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict, deque
import json
from dataclasses import dataclass, asdict
from app.utils.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@dataclass
class RequestMetrics:
    """Request metrics data class"""
    endpoint: str
    method: str
    status_code: int
    response_time: float
    timestamp: datetime
    user_agent: str
    ip_address: str
    file_size: Optional[int] = None
    error_message: Optional[str] = None

@dataclass
class SystemMetrics:
    """System metrics data class"""
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    active_connections: int
    timestamp: datetime

class MonitoringService:
    """Application monitoring and metrics service"""
    
    def __init__(self):
        self.request_metrics: deque = deque(maxlen=1000)  # Keep last 1000 requests
        self.system_metrics: deque = deque(maxlen=100)    # Keep last 100 system snapshots
        self.error_counts: defaultdict = defaultdict(int)
        self.endpoint_stats: defaultdict = defaultdict(lambda: {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0.0,
            "total_response_time": 0.0
        })
        
        # Performance thresholds
        self.thresholds = {
            "response_time_warning": 2.0,  # seconds
            "response_time_critical": 5.0,  # seconds
            "cpu_warning": 70.0,           # percent
            "cpu_critical": 90.0,          # percent
            "memory_warning": 80.0,        # percent
            "memory_critical": 95.0,       # percent
            "error_rate_warning": 0.05,    # 5%
            "error_rate_critical": 0.10    # 10%
        }
        
        # Start system monitoring
        self._start_system_monitoring()
    
    def _start_system_monitoring(self):
        """Start periodic system monitoring"""
        import threading
        import time
        
        def monitor_system():
            while True:
                try:
                    self._record_system_metrics()
                    time.sleep(30)  # Record every 30 seconds
                except Exception as e:
                    logger.error(f"System monitoring error: {e}")
                    time.sleep(60)  # Wait longer on error
        
        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=monitor_system, daemon=True)
        monitor_thread.start()
    
    def record_request(self, request_metrics: RequestMetrics):
        """Record request metrics"""
        try:
            # Add to request history
            self.request_metrics.append(request_metrics)
            
            # Update endpoint statistics
            endpoint_key = f"{request_metrics.method} {request_metrics.endpoint}"
            stats = self.endpoint_stats[endpoint_key]
            
            stats["total_requests"] += 1
            stats["total_response_time"] += request_metrics.response_time
            
            if 200 <= request_metrics.status_code < 400:
                stats["successful_requests"] += 1
            else:
                stats["failed_requests"] += 1
                self.error_counts[request_metrics.status_code] += 1
            
            # Update average response time
            stats["avg_response_time"] = stats["total_response_time"] / stats["total_requests"]
            
            # Log slow requests
            if request_metrics.response_time > self.thresholds["response_time_warning"]:
                logger.warning(f"Slow request: {endpoint_key} took {request_metrics.response_time:.2f}s")
            
            # Log errors
            if request_metrics.status_code >= 400:
                logger.error(f"Request error: {endpoint_key} - {request_metrics.status_code}")
                if request_metrics.error_message:
                    logger.error(f"Error details: {request_metrics.error_message}")
                    
        except Exception as e:
            logger.error(f"Error recording request metrics: {e}")
    
    def _record_system_metrics(self):
        """Record system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            
            # Active connections (simplified)
            active_connections = len(self.request_metrics)
            
            system_metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_usage_percent=disk_usage_percent,
                active_connections=active_connections,
                timestamp=datetime.utcnow()
            )
            
            self.system_metrics.append(system_metrics)
            
            # Log warnings for high resource usage
            if cpu_percent > self.thresholds["cpu_warning"]:
                logger.warning(f"High CPU usage: {cpu_percent:.1f}%")
            
            if memory_percent > self.thresholds["memory_warning"]:
                logger.warning(f"High memory usage: {memory_percent:.1f}%")
                
        except Exception as e:
            logger.error(f"Error recording system metrics: {e}")
    
    def get_request_metrics(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get request metrics for the last N hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        metrics = []
        for metric in self.request_metrics:
            if metric.timestamp >= cutoff_time:
                metrics.append(asdict(metric))
        
        return metrics
    
    def get_system_metrics(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get system metrics for the last N hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        metrics = []
        for metric in self.system_metrics:
            if metric.timestamp >= cutoff_time:
                metrics.append(asdict(metric))
        
        return metrics
    
    def get_endpoint_statistics(self) -> Dict[str, Any]:
        """Get endpoint statistics"""
        return dict(self.endpoint_stats)
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        total_requests = sum(stats["total_requests"] for stats in self.endpoint_stats.values())
        total_errors = sum(self.error_counts.values())
        
        return {
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": total_errors / total_requests if total_requests > 0 else 0,
            "error_breakdown": dict(self.error_counts),
            "endpoint_errors": {
                endpoint: stats["failed_requests"] 
                for endpoint, stats in self.endpoint_stats.items()
                if stats["failed_requests"] > 0
            }
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        # Calculate response time percentiles
        response_times = [m.response_time for m in self.request_metrics]
        response_times.sort()
        
        if response_times:
            p50 = response_times[len(response_times) // 2]
            p95 = response_times[int(len(response_times) * 0.95)]
            p99 = response_times[int(len(response_times) * 0.99)]
        else:
            p50 = p95 = p99 = 0.0
        
        # Get latest system metrics
        latest_system = self.system_metrics[-1] if self.system_metrics else None
        
        return {
            "response_time": {
                "average": sum(response_times) / len(response_times) if response_times else 0.0,
                "p50": p50,
                "p95": p95,
                "p99": p99,
                "min": min(response_times) if response_times else 0.0,
                "max": max(response_times) if response_times else 0.0
            },
            "system": {
                "cpu_percent": latest_system.cpu_percent if latest_system else 0.0,
                "memory_percent": latest_system.memory_percent if latest_system else 0.0,
                "disk_usage_percent": latest_system.disk_usage_percent if latest_system else 0.0,
                "active_connections": latest_system.active_connections if latest_system else 0
            },
            "requests": {
                "total_requests": len(self.request_metrics),
                "requests_per_minute": self._calculate_requests_per_minute(),
                "unique_endpoints": len(self.endpoint_stats)
            }
        }
    
    def _calculate_requests_per_minute(self) -> float:
        """Calculate requests per minute"""
        if not self.request_metrics:
            return 0.0
        
        # Get requests from last minute
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
        recent_requests = sum(1 for m in self.request_metrics if m.timestamp >= one_minute_ago)
        
        return recent_requests
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        performance = self.get_performance_summary()
        error_stats = self.get_error_statistics()
        
        # Determine health status
        health_status = "healthy"
        warnings = []
        critical_issues = []
        
        # Check response time
        avg_response_time = performance["response_time"]["average"]
        if avg_response_time > self.thresholds["response_time_critical"]:
            health_status = "critical"
            critical_issues.append(f"High response time: {avg_response_time:.2f}s")
        elif avg_response_time > self.thresholds["response_time_warning"]:
            health_status = "warning"
            warnings.append(f"Slow response time: {avg_response_time:.2f}s")
        
        # Check error rate
        error_rate = error_stats["error_rate"]
        if error_rate > self.thresholds["error_rate_critical"]:
            health_status = "critical"
            critical_issues.append(f"High error rate: {error_rate:.2%}")
        elif error_rate > self.thresholds["error_rate_warning"]:
            health_status = "warning"
            warnings.append(f"Elevated error rate: {error_rate:.2%}")
        
        # Check system resources
        system = performance["system"]
        if system["cpu_percent"] > self.thresholds["cpu_critical"]:
            health_status = "critical"
            critical_issues.append(f"Critical CPU usage: {system['cpu_percent']:.1f}%")
        elif system["cpu_percent"] > self.thresholds["cpu_warning"]:
            warnings.append(f"High CPU usage: {system['cpu_percent']:.1f}%")
        
        if system["memory_percent"] > self.thresholds["memory_critical"]:
            health_status = "critical"
            critical_issues.append(f"Critical memory usage: {system['memory_percent']:.1f}%")
        elif system["memory_percent"] > self.thresholds["memory_warning"]:
            warnings.append(f"High memory usage: {system['memory_percent']:.1f}%")
        
        return {
            "status": health_status,
            "timestamp": datetime.utcnow().isoformat(),
            "warnings": warnings,
            "critical_issues": critical_issues,
            "performance": performance,
            "error_stats": error_stats
        }
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format"""
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "performance_summary": self.get_performance_summary(),
            "endpoint_statistics": self.get_endpoint_statistics(),
            "error_statistics": self.get_error_statistics(),
            "health_status": self.get_health_status(),
            "recent_requests": self.get_request_metrics(hours=1),
            "system_metrics": self.get_system_metrics(hours=1)
        }
        
        if format.lower() == "json":
            return json.dumps(data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def clear_old_metrics(self, days: int = 7):
        """Clear metrics older than specified days"""
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        # Clear old request metrics
        self.request_metrics = deque(
            [m for m in self.request_metrics if m.timestamp >= cutoff_time],
            maxlen=1000
        )
        
        # Clear old system metrics
        self.system_metrics = deque(
            [m for m in self.system_metrics if m.timestamp >= cutoff_time],
            maxlen=100
        )
        
        logger.info(f"Cleared metrics older than {days} days")

# Global monitoring service instance
monitoring_service = MonitoringService() 
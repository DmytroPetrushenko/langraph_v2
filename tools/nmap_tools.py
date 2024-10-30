import nmap
from typing import List, Optional
from langchain_core.tools import tool


@tool
def tool_based_on_nmap(in_hosts: str, in_ports: Optional[str] = None, in_arguments: str = "-sV") -> str:
    """
    A tool to scan a target host using Nmap.

    Args:
        in_hosts (str): The target host or hosts to be scanned.
        in_ports (Optional[str]): The specific ports to scan. Defaults to None, which scans common ports.
        in_arguments (str): Additional arguments for Nmap. Defaults to "-sV" to detect service versions.

    Returns:
        str: The scan results as a formatted string or an error message if an exception occurs.
    """
    try:
        # Initialize the Nmap scanner
        scanner = nmap.PortScanner()
        result_list: List[str] = []

        # Run the Nmap scan with the provided target, ports, and arguments
        scanner.scan(
            hosts=in_hosts,
            ports=in_ports,
            arguments=in_arguments
        )

        # Collect the results from the scan
        for host in scanner.all_hosts():
            result_list.append(f"Host: {host}")
            result_list.append(f"State: {scanner[host].state()}")
            for proto in scanner[host].all_protocols():
                result_list.append(f"Protocol: {proto}")
                ports = scanner[host][proto].keys()
                for port in ports:
                    result_list.append(f"Port: {port}, State: {scanner[host][proto][port]['state']}")


        # Return the results as a single string
        result_str = '\n'.join(result_list)
        answer_template = f"Targets: {hosts}, Ports: {ports}, Arguments: {arguments}, Scan result: {result_str if result_str else 'No results'}"

        return answer_template

    except Exception as e:
        # Return the error message in a format that AI can handle
        return f"Error occurred during Nmap scan: {str(e)}"

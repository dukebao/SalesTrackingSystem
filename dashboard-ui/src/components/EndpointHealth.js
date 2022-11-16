import React, { useEffect, useState } from 'react'
import '../App.css';

export default function EndpointHealth() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        // fetch(`http://steven-kafka-apple-banana.eastus.cloudapp.azure.com:8100/stats`)
        fetch(`http://steven-kafka-apple-banana.eastus.cloudapp.azure.com:8120/healthcheck`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                console.log(result)
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 5000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Endpoint healthcheck</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Receiver</th>
							<th>Storage</th>
                            <th>Processing</th>
                            <th>Audit</th>
						</tr>
						<tr>
							<td>{stats['receiverStats']}</td>
							<td>{stats['storageStats']}</td>
                            <td>{stats['processingStats']}</td>
                            <td>{stats['auditStats']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['Last Update']}</h3>
            </div>
        )
    }
}

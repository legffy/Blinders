
export function Dashboard()
{
   return (<div>
        <p>Logged in</p>
        <button onClick={() =>{
            chrome.runtime.sendMessage({ type: "LOGOUT"});
            window.close();
        }}>
            Sign out
        </button>
    </div> )
}

type Props = {
    onLogin: () => void;
};
export default function Signedout({ onLogin }: Props)
{
    return (
        <div className="min-h-screen max-w-screen flex flex-col items-center justify-center text-lg">
            <h1 className="text-2xl">Blinders</h1>
            <button className="bg-white hover:bg-gray-100 border-2 border-black text-black p-3"
            onClick={() => {
                console.log("hello my friend")
                onLogin();
            }} >
               Login in/Sign up
            </button>
        </div>
    )
}
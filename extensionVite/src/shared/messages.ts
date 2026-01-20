export type AuthStartMsg = {
    type: "AUTH_START";
}
export type AuthStatus = {
    type: "AUTH_STATUS"
    force: boolean
}

export type ExtensionMessage =
| AuthStartMsg | AuthStatus
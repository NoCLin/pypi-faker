import {ExecutionContext} from "@cloudflare/workers-types";
import { Env } from 'hono';
import {app} from './routers'


export default {
    fetch(request: Request, env: Env, ctx: ExecutionContext) {
        return app.fetch(request, env, ctx)
    },
}

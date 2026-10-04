import {handleConversationRequest} from '../../../lib/server/conversation-proxy';
type Context = {params:Promise<{path?:string[]}>};
async function handle(req:Request,context:Context) {
  const {path=[]}=await context.params;
  return handleConversationRequest(req,path);
}
export {handle as GET,handle as POST,handle as DELETE};

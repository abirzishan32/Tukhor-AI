import type { User as SupabaseUser } from "@supabase/supabase-js";

export type SignUpOptions = {
    userName: string;
    email: string;
    password: string;
    repeatPassword: string;
}

export type User = SupabaseUser & {
    profile: {
        id: string;
        userName: string;
        email: string;
    };
}
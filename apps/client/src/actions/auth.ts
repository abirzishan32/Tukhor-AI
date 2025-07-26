'use server';

import { createClient } from "@/lib/supabase/server";
import { revalidatePath } from "next/cache";
import prisma from "@/lib/prisma";
import type { User,  SignUpOptions } from "@/types";

export async function signUp({
    userName,
    email,
    password,
    repeatPassword,
}: SignUpOptions) {
    const supabase = await createClient();

    if (password !== repeatPassword) {
        throw new Error("Passwords do not match");
    }

    const profileExists = await prisma.profile.findUnique({
        where: { userName },
    });

    if (profileExists) {
        throw new Error("Username already exists");
    }

    const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
            data: { userName },
            emailRedirectTo: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard`,
        },
    });

    if (error) {
        throw error;
    }

    console.log("Supabase sign up data:", data);

    const user=data.user;

    if (!user) {
        throw new Error("User creation failed");
    }

    await prisma.profile.create({
        data: {
            id: user.id,
            userName,
            email,
        },
    });

    revalidatePath("/auth/sign-up-success");
}

export async function getUser() {
    const supabase = await createClient();

    const { data: { user } } = await supabase.auth.getUser();

    if (!user) {
        return null;
    }

    const profile = await prisma.profile.findUnique({
        where: { id: user.id },
    });

    if (!profile) {
        throw new Error("Profile not found");
    }

    return {
        ...user,
        profile: profile as User["profile"]
    } as User;
}
